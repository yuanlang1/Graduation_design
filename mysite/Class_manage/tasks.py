# -*- coding = utf-8 -*-
import cv2
import ffmpeg
import json
import math
import os

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from ultralytics import YOLO

from home.models import CourseInfo, ClassroomStatus, RecognitionResult


@shared_task
def add(x, y):
    return x + y


@shared_task
def process_classroom_detection(data):
    class_name = data.get('className', '').strip()
    course_name = data.get('courseName', '').strip()
    teacher_name = data.get('teacherName', '').strip()
    url = data.get('rawpic', '').strip()

    course = CourseInfo.objects.filter(
        course_name=course_name,
        class_name=class_name,
        teacher_name=teacher_name
    ).first()

    if not course:
        return {'code': 404, 'msg': '课程不存在'}

    course_id = course.id
    class_status = ClassroomStatus.objects.filter(course_id=course_id).first()
    now = timezone.now().replace(microsecond=0)

    raw_video_path = os.path.join(settings.BASE_DIR, "static", "rawpic", url.lstrip('/'))
    if not os.path.exists(raw_video_path):
        return {'code': 400, 'msg': '原始图片文件不存在'}

    resultpic_base = os.path.join(settings.BASE_DIR, "static", "resultpic")
    video_basename = os.path.splitext(os.path.basename(raw_video_path))[0]
    video_folder = os.path.join(resultpic_base, video_basename)

    result_json_dir = os.path.join(settings.BASE_DIR, "static", "result_json")

    result_video_name = f"{video_basename}.avi"
    result_video_path = os.path.join(video_folder, result_video_name)
    json_name = f"{video_basename}.json"
    json_path = os.path.join(result_json_dir, json_name)

    behavior_classes = ["dx", "dk", "tt", "zt", "js", "zl", "xt"]
    weights = {"dx": 4, "dk": 0, "tt": 1, "zt": -2, "js": 3, "zl": -1, "xt": 4}
    total_students = 60

    try:
        model = YOLO("yolo/best.pt")
        results = model(
            raw_video_path,
            save=True,
            project=video_folder,
            name=".",  # 强制输出到 video_folder 下
            stream=True
        )
    except Exception as e:
        return {'code': 500, 'msg': f'YOLOv8 检测失败: {e}'}

    json_result = []
    action_count_per_frame = []
    frame_idx = 0

    try:
        for result in results:
            action_counter = {action: 0 for action in behavior_classes}
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                if 0 <= class_id < len(behavior_classes):
                    behavior = behavior_classes[class_id]
                    action_counter[behavior] += 1
            json_result.append({'frame': frame_idx, 'action_count': action_counter})
            action_count_per_frame.append(action_counter)
            frame_idx += 1

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=4)
    except Exception as e:
        return {'code': 500, 'msg': f'行为识别 JSON 生成失败: {e}'}

    try:
        cap = cv2.VideoCapture(raw_video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        total_frames = len(action_count_per_frame)
        interval_seconds = 30
        sampled_scores = []
        num_samples = math.floor(total_frames / (fps * interval_seconds))

        for i in range(num_samples):
            sample_index = int(i * interval_seconds * fps)
            if sample_index >= total_frames:
                break
            frame_actions = action_count_per_frame[sample_index]
            frame_probabilities = {action: frame_actions.get(action, 0) / total_students for action in behavior_classes}
            frame_score = sum(frame_probabilities[action] * weights[action] for action in behavior_classes)
            sampled_scores.append(frame_score)

        final_score = round(sum(sampled_scores) / len(sampled_scores), 2) if sampled_scores else 0.0
    except Exception as e:
        return {'code': 500, 'msg': f'30秒抽帧统计失败: {e}'}

    estimate = final_score

    try:
        mp4_video_name = f"{video_basename}.mp4"
        mp4_video_path = os.path.join(video_folder, mp4_video_name)
        ffmpeg.input(result_video_path).output(mp4_video_path).run()
        result_video_url = f"/{video_basename}/{mp4_video_name}"
    except Exception as e:
        return {'code': 500, 'msg': f'视频格式转换失败: {e}'}

    json_url = f"/{json_name}"

    # 保存检测结果
    recognition = RecognitionResult(
        class_id=course_id,
        estimate=estimate,
        dtime=now,
        rawpic=url,
        resultpic=result_video_url,
        result=json_url
    )
    recognition.save()

    if class_status:
        class_status.estimate = estimate
        class_status.dtime = now
        class_status.save()
    else:
        class_status = ClassroomStatus(
            course_id=course_id,
            estimate=estimate,
            dtime=now
        )
        class_status.save()

    return {'code': 200, 'msg': '检测完成', 'data': {'id': course_id, 'estimate': estimate}}
