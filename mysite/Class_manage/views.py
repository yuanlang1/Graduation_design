import json
import time
import shutil

from PIL import Image
from django.core.files import File
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone  # 确保已导入 timezone
from home.models import CourseInfo, TeacherInfo, ClassroomStatus, RecognitionResult
import datetime
import os
from django.core.files.storage import FileSystemStorage
# from ultralytics import YOLO  # 临时注释 YOLOv8 库导入
# import cv2
# import numpy as np
import random
from django.conf import settings


def upload_image(request):
    if request.method == 'POST':
        try:
            # 假设前端通过 multipart/form-data 上传文件，字段名为 "file"
            file = request.FILES.get("file")
            if not file:
                return JsonResponse({'code': 400, 'msg': '文件未上传'}, status=400)

            # 获取媒体类型（从 formData 或文件扩展名推断）
            # media_type = request.POST.get('mediaType', 'image')  # 前端传入的媒体类型（image 或 video）
            file_name = file.name
            file_extension = os.path.splitext(file_name.lower())[1]  # 获取文件扩展名（如 .jpg, .mp4）

            # 验证文件类型（支持图片和视频）
            allowed_image_extensions = ['.jpg', '.jpeg', '.png']
            allowed_video_extensions = ['.mp4', '.avi', '.mov', '.wmv']  # 支持常见视频格式
            if file_extension in allowed_image_extensions:
                media_type = 'image'
            elif file_extension in allowed_video_extensions:
                media_type = 'video'
            else:
                return JsonResponse({'code': 400,
                                     'msg': '不支持的文件类型，请上传图片（.jpg, .jpeg, .png）或视频（.mp4, .avi, .mov, .wmv）'},
                                    status=400)

            # 使用 FileSystemStorage 存储媒体到 static/rawpic
            fs = FileSystemStorage(location=os.path.join(os.path.join(settings.BASE_DIR, "static"), 'rawpic'))

            # 生成唯一的文件名（时间戳 + 随机数 + 原始文件名）
            timestamp = int(time.time() * 1000)  # 使用毫秒级时间戳更精确
            random_num = random.randint(0, 9999)  # 增加随机数范围，避免冲突
            base_name = os.path.splitext(file_name)[0]  # 提取原始文件名（不含扩展名）
            unique_file_name = f"{timestamp}_{random_num}_{base_name}{file_extension}"

            # 保存文件
            fs.save(unique_file_name, file)
            # 构造媒体 URL
            media_url = fs.url(unique_file_name)

            return JsonResponse({
                'code': 200,
                'data': {'url': media_url},  # 返回媒体 URL，匹配前端 data.url
                'msg': '上传成功',
                'mediaType': media_type  # 返回媒体类型，便于前端处理
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'上传失败：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 POST 请求'}, status=405)


def classrooms(request):
    try:
        query = """
                    SELECT 
                        ci.id,
                        ci.course_name,
                        ci.class_name,
                        ci.teacher_name,
                        ci.course_time,
                        ci.stage,
                        ci.location,
                        re.rawpic,
                        re.resultpic,
                        re.dtime,
                        re.estimate
                    FROM 
                        home_courseinfo ci,
                        home_classroomstatus cs,
                        home_recognitionresult re
                    WHERE 
                        ci.id = cs.course_id
                        AND re.class_id = cs.course_id
                """
        # 执行查询
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
        except Exception as e:
            print(e)
        print(1)

        filtered_rows = []

        if request.body:
            try:
                class_name = request.GET.get('className', '').strip()
                course_name = request.GET.get('courseName', '').strip()
                teacher_name = request.GET.get('teacherName', '').strip()
                course_time = request.GET.get('dtime', None).strip()
                location = request.GET.get('location', '').strip()
                stage = request.GET.get('stage', 1)
            except Exception as e:
                print(e)

            print("class_name:", class_name)
            print("course_name:", course_name)
            print("teacher_name:", teacher_name)
            print("course_time:", course_time)
            print("location:", location)
            print("stage:", stage)

            for row in rows:
                if (course_name and course_name.lower() not in row[1].lower()) or \
                        (class_name and class_name.lower() not in row[2].lower()) or \
                        (teacher_name and teacher_name.lower() not in row[3].lower()) or \
                        (course_time and course_time.lower() not in row[4].lower()) or \
                        (stage and stage.lower() not in row[5].lower()) or \
                        (location and location.lower() not in row[6].lower()):
                    continue
                filtered_rows.append({
                    'id': row[0],
                    'course_name': row[1],
                    'class_name': row[2],
                    'teacher_name': row[3],
                    'course_time': row[4],
                    'stage': row[5],
                    'location': row[6],
                    'detect_time': row[9],
                    'estimate': row[10],
                    'rawpic': row[7],
                    'resultpic': row[8]
                })
            print(filtered_rows)

        else:
            for row in rows:
                filtered_rows.append({
                    'id': row[0],
                    'course_name': row[1],
                    'class_name': row[2],
                    'teacher_name': row[3],
                    'course_time': row[4],
                    'stage': row[5],
                    'location': row[6],
                    'detect_time': row[9],
                    'estimate': row[10],
                    'rawpic': row[7],
                    'resultpic': row[8]
                })
        return JsonResponse({
            'code': 200,
            'data': filtered_rows
        })
    except Exception as e:
        print(e)
        return JsonResponse({'code': 500, 'msg': f'服务器错误，请稍后重试：{str(e)}'}, status=500)


def Add_classrooms(request):
    data = json.loads(request.body.decode('utf-8'))
    class_name = data.get('className', '').strip()
    course_name = data.get('courseName', '').strip()
    teacher_name = data.get('teacherName', '').strip()
    course_time = data.get('dtime', '').strip()
    url = data.get('rawpic', '').strip()
    print(1)
    print("class_name:", class_name)
    print("course_name:", course_name)
    print("teacher_name:", teacher_name)
    print("course_time:", course_time)
    print("url:", url)

    course = CourseInfo.objects.filter(
        course_name=course_name,
        class_name=class_name,
        teacher_name=teacher_name
    ).first()

    print("course:", course)

    # 存在该课程
    if course:
        print("存在该课程")
        course_id = course.id
        class_status = ClassroomStatus.objects.filter(course_id=course_id).first()
        print("class_status", class_status)
        estimate = 100
        now = timezone.now()

        time = now.replace(microsecond=0)
        print(time)

        # 复制 rawpic 文件到 static/resultpic 目录
        rawpic_path = os.path.join(settings.BASE_DIR, "static", "rawpic", url.lstrip('/'))
        if not os.path.exists(rawpic_path):
            return JsonResponse({'code': 400, 'msg': '原始图片文件不存在'}, status=400)
        print("rawpic_path:", rawpic_path)

        # 确保 static/resultpic 目录存在
        resultpic_path = os.path.join(settings.BASE_DIR, "static", "resultpic")
        if not os.path.exists(resultpic_path):
            os.makedirs(resultpic_path)
        print("resultpic_dir:", resultpic_path)

        shutil.copy2(rawpic_path, resultpic_path)

        # 使用 FileSystemStorage 管理 resultpic 文件
        fs_result = FileSystemStorage(location=resultpic_path)
        resultpic_url = fs_result.url(url)

        # 创建新的检测结果
        recognition = RecognitionResult(
            class_id=course_id,
            estimate=estimate,
            dtime=time,
            rawpic=url,
            resultpic=resultpic_url
        )
        try:
            recognition.save()
        except Exception as e:
            print("1", e)
        # 存在该课堂
        if class_status:
            class_status.estimate = estimate
            class_status.dtime = time
            try:
                class_status.save()
            except Exception as e:
                print("2", e)
        else:
            class_status = ClassroomStatus(
                course_id=course_id,
                estimate=estimate,
                dtime=time
            )
            try:
                class_status.save()
            except Exception as e:
                print("2", e)

        return JsonResponse({
            'code': 200,
            'msg': '添加成功',
            'data': {'id': course_id}
        })

    else:
        return JsonResponse({'code': 404, 'msg': '添加失败'}, status=404)


def Delete_classrooms(request, id):
    data = json.loads(request.body.decode('utf-8'))
    dtime = data.get('dtime', '').strip()
    # 将日期格式中的斜杠替换为连字符
    dtime_str = dtime.replace('/', '-')
    print("id:", id)
    print("time:", dtime_str)

    try:
        time = datetime.datetime.strptime(dtime_str, '%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        print(e)
    print("time:", time)

    course = CourseInfo.objects.filter(id=id).first()
    print(course)

    status = ClassroomStatus.objects.filter(course_id=id).first()
    print(status)
    print(1)
    recogntion = RecognitionResult.objects.get(
        class_id=id,
        dtime=time
    )
    print(2)
    recogntion.delete()
    print(3)
    recogntion_new = RecognitionResult.objects.filter(class_id=id).order_by('dtime').first()
    print(4)
    if recogntion_new:
        status.dtime = recogntion_new.dtime
    print(5)
    status.save()

    return JsonResponse({
        'code': 200,
        'msg': '删除成功'
    })
