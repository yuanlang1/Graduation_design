# views.py (位于 home 目录下)
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


# def upload_image(request):
#     """
#     接收前端选择的课程媒体（图片或视频，字段名为 "file"），存储在 static/rawpic 目录，使用 FileSystemStorage 返回媒体的 URL。
#     保证文件名不重复：使用时间戳 + 随机数 + 原始文件名。
#     支持的媒体类型：图片（.jpg, .png, .jpeg）和视频（.mp4, .avi, .mov 等）。
#     """
#     if request.method == 'POST':
#         try:
#             # 假设前端通过 multipart/form-data 上传文件，字段名为 "file"
#             file = request.FILES.get("file")
#             if not file:
#                 return JsonResponse({'code': 400, 'msg': '文件未上传'}, status=400)
#
#             # 获取媒体类型（从 formData 或文件扩展名推断）
#             media_type = request.POST.get('mediaType', 'image')  # 前端传入的媒体类型（image 或 video）
#             file_name = file.name
#             file_extension = os.path.splitext(file_name.lower())[1]  # 获取文件扩展名（如 .jpg, .mp4）
#
#             # 验证文件类型（支持图片和视频）
#             allowed_image_extensions = ['.jpg', '.jpeg', '.png']
#             allowed_video_extensions = ['.mp4', '.avi', '.mov', '.wmv']  # 支持常见视频格式
#             if file_extension in allowed_image_extensions:
#                 media_type = 'image'
#             elif file_extension in allowed_video_extensions:
#                 media_type = 'video'
#             else:
#                 return JsonResponse({'code': 400,
#                                      'msg': '不支持的文件类型，请上传图片（.jpg, .jpeg, .png）或视频（.mp4, .avi, .mov, .wmv）'},
#                                     status=400)
#
#             # 使用 FileSystemStorage 存储媒体到 static/rawpic
#             fs = FileSystemStorage(location=os.path.join(os.path.join(settings.BASE_DIR, "static"), 'rawpic'))
#
#             # 生成唯一的文件名（时间戳 + 随机数 + 原始文件名）
#             timestamp = int(time.time() * 1000)  # 使用毫秒级时间戳更精确
#             random_num = random.randint(0, 9999)  # 增加随机数范围，避免冲突
#             base_name = os.path.splitext(file_name)[0]  # 提取原始文件名（不含扩展名）
#             unique_file_name = f"{timestamp}_{random_num}_{base_name}{file_extension}"
#
#             # 保存文件
#             fs.save(unique_file_name, file)
#             # 构造媒体 URL
#             media_url = fs.url(unique_file_name)
#
#             return JsonResponse({
#                 'code': 200,
#                 'data': {'url': media_url},  # 返回媒体 URL，匹配前端 data.url
#                 'msg': '上传成功',
#                 'mediaType': media_type  # 返回媒体类型，便于前端处理
#             })
#         except Exception as e:
#             return JsonResponse({'code': 500, 'msg': f'上传失败：{str(e)}'}, status=500)
#     return JsonResponse({'code': 405, 'msg': '仅支持 POST 请求'}, status=405)


def courses(request):
    """
    查询课程信息，支持按课程名称、课堂名称、教师姓名、节数、上课地址和上课时间筛选。
    返回数据包括课程名称、课堂名称、教师、上课时间、节数、上课地址和专注度分数。
    """
    if request.method == 'GET':
        try:
            # 获取查询参数
            course_name = request.GET.get('courseName', '').strip()
            class_name = request.GET.get('className', '').strip()
            teacher_name = request.GET.get('teacherName', '').strip()
            stage = request.GET.get('stage', '').strip()  # 新增：节数
            location = request.GET.get('location', '').strip()  # 新增：上课地址
            dtime = request.GET.get('dtime', '').strip()  # 新增：上课时间

            print(course_name)
            # 查询 CourseInfo 表作为主要数据源
            query = CourseInfo.objects.all()

            # 按课程名称筛选
            if course_name:
                query = query.filter(course_name__icontains=course_name)

            # 按课堂名称筛选
            if class_name:
                query = query.filter(class_name__icontains=class_name)

            # 按教师姓名筛选
            if teacher_name:
                query = query.filter(teacher_name__icontains=teacher_name)

            # 按节数筛选（精确匹配）
            if stage:
                try:
                    stage_value = int(stage)
                    query = query.filter(stage=stage_value)
                except ValueError:
                    return JsonResponse({'code': 400, 'msg': '节数必须为整数'}, status=400)

            # 按上课地址筛选
            if location:
                query = query.filter(location__icontains=location)

            # 按上课时间筛选（精确匹配）
            if dtime:
                try:
                    dtime_dt = datetime.datetime.strptime(dtime, '%Y-%m-%d %H:%M:%S')
                    query = query.filter(course_time=dtime_dt)
                except ValueError:
                    return JsonResponse({'code': 400, 'msg': '时间格式错误，请输入 YYYY-MM-DD HH:MM:SS'}, status=400)

            # 构造返回数据，关联 ClassroomStatus 获取 estimate 和 dtime
            course_list = []
            for course in query:
                course_list.append({
                    'id': course.id,  # 使用 CourseInfo 的 id 作为课程号
                    'course_name': course.course_name,
                    'class_name': course.class_name,
                    'teacher_name': course.teacher_name,
                    'dtime': course.course_time,
                    'stage': course.stage,
                    'location': course.location
                })

            return JsonResponse({
                'code': 200,
                'data': course_list
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'服务器错误，请稍后重试：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 GET 请求'}, status=405)


def delete_courses(request, id):
    """
    删除指定课程（通过 course_id），路径为 /Course_manage/Delete_courses/<int:id>/。
    接收前端传送的 course_name 和 class_name，删除 CourseInfo、ClassroomStatus 和 RecognitionResult 中匹配的记录，
    同时删除 static/rawpic 和 static/resultpic 文件中对应的文件。
    """
    if request.method == 'DELETE':
        try:
            # 解析请求体中的 JSON 数据
            data = json.loads(request.body.decode('utf-8'))
            course_name = data.get('course_name', '').strip()
            class_name = data.get('class_name', '').strip()

            # 验证 course_name 和 class_name 是否提供
            if not course_name or not class_name:
                return JsonResponse({'code': 400, 'msg': 'course_name 和 class_name 不能为空'}, status=400)

            # 查询并删除 CourseInfo 记录（因为 course_id 是 CourseInfo 的 id）
            try:
                course = CourseInfo.objects.get(id=id)
                course_name_db = course.course_name
                class_name_db = course.class_name
                if course_name != course_name_db or class_name != class_name_db:
                    return JsonResponse({'code': 400, 'msg': '课程名称或课堂名称不匹配'}, status=400)
            except CourseInfo.DoesNotExist:
                return JsonResponse({'code': 404, 'msg': '课程不存在'}, status=404)

            # 删除与 CourseInfo 关联的 ClassroomStatus 记录
            try:
                classroom_status = ClassroomStatus.objects.get(course_id=id)
                classroom_status.delete()
            except ClassroomStatus.DoesNotExist:
                pass  # 如果 ClassroomStatus 不存在，跳过

            # 删除 RecognitionResult 中匹配 class_id 的记录
            recognition_results = RecognitionResult.objects.filter(class_id=id)
            for result in recognition_results:
                # 删除与 RecognitionResult 关联的 rawpic 和 resultpic 文件
                if result.rawpic:
                    rawpic_path = os.path.join(settings.BASE_DIR, "static", "rawpic", result.rawpic.lstrip('/'))
                    if os.path.exists(rawpic_path):
                        os.remove(rawpic_path)
                if result.resultpic:
                    resultpic_path = os.path.join(settings.BASE_DIR, "static", "resultpic",
                                                  result.resultpic.lstrip('/'))
                    if os.path.exists(resultpic_path):
                        os.remove(resultpic_path)
            recognition_results.delete()

            # 删除 CourseInfo 记录
            course.delete()

            return JsonResponse({
                'code': 200,
                'msg': '删除成功'
            })
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'}, status=400)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'删除失败，请稍后重试：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 DELETE 请求'}, status=405)


def add_courses(request):
    try:
        # 解析请求体中的 JSON 数据
        data = json.loads(request.body.decode('utf-8'))
        class_name = data.get('className', '').strip()
        course_name = data.get('courseName', '').strip()
        teacher_name = data.get('teacherName', '').strip()
        dtime = data.get('dtime', None)
        location = data.get('location', '').strip()  # 上课地址
        stage = data.get('stage', 1)  # 节数，默认值为 1
        # estimate 从前端获取的值被固定为 100
        estimate = '100'  # 固定为 100

        # 验证必填字段
        if not class_name or not course_name or not teacher_name or not dtime or not location:
            return JsonResponse({'code': 400, 'msg': '必填字段不能为空'}, status=400)

        # 调试信息
        print("class_name:", class_name)
        print("course_name:", course_name)
        print("teacher_name:", teacher_name)
        print("dtime from frontend:", dtime)  # 调试前端传入的 dtime
        print("location:", location)
        print("stage:", stage)

        # 解析前端传入的 dtime 字符串为 datetime 对象
        try:
            # 确保 dtime 格式为 YYYY-MM-DD HH:MM:SS
            course_dtime = datetime.datetime.strptime(dtime, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print("Time parsing error:", e)
            return JsonResponse({'code': 400, 'msg': '时间格式错误，请输入 YYYY-MM-DD HH:MM:SS'}, status=400)
        # # 验证节数为正整数
        # if stage and (not isinstance(stage, int) or stage <= 0):
        #     return JsonResponse({'code': 400, 'msg': '节数必须为正整数'}, status=400)
        # 调试转换后的时间
        print("Converted course dtime:", course_dtime)

        # 1. 查询 CourseInfo 中是否存在 class_name, course_name, teacher_name, course_time 相同的记录
        existing_course = CourseInfo.objects.filter(
            class_name=class_name,
            course_name=course_name,
            teacher_name=teacher_name,
            course_time=course_dtime
        ).first()

        print(2)

        if existing_course:
            print("existing Course found")
            return JsonResponse({'code': 404, 'msg': '已经有该课程'}, status=404)
        else:
            # 3. 如果不存在，创建新的 CourseInfo、ClassroomStatus 和 RecognitionResult
            print("No existing Course found, creating new records")

            # 创建新的 CourseInfo
            course = CourseInfo(
                course_name=course_name,
                class_name=class_name,
                teacher_name=teacher_name,
                location=location,
                stage=stage,
                course_time=course_dtime
            )
            course.save()
            course_id = course.id
            print("Created new CourseInfo, ID:", course_id)

            return JsonResponse({
                'code': 200,
                'msg': '操作成功',
                'data': {'id': course_id}  # 返回 CourseInfo 的 id
            })

    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'}, status=400)
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': f'服务器错误，请稍后重试：{str(e)}'}, status=500)


def update_courses(request, id):
    """
    更新指定课程（通过 id），路径为 /Course_manage/<id>/。
    """
    if request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            class_name = data.get('className', '').strip()
            course_name = data.get('courseName', '').strip()
            teacher_name = data.get('teacherName', '').strip()
            dtime = data.get("dtime").strip()
            location = data.get('location', '').strip()
            stage = data.get('stage', 1)

            print("class_name", class_name)
            print("course_name", course_name)
            print("teacher_name", teacher_name)

            # 验证必填字段
            if not class_name or not course_name or not teacher_name:
                return JsonResponse({'code': 400, 'msg': '必填字段不能为空'}, status=400)

            # 更新或创建 CourseInfo 和 TeacherInfo（如果需要）
            course = CourseInfo.objects.get(id=id)

            course.course_name = course_name
            course.class_name = class_name
            course.teacher_name = teacher_name
            course.course_time = datetime.datetime.strptime(dtime, '%Y-%m-%d %H:%M:%S')
            course.location = location
            course.stage = stage

            course.save()

            return JsonResponse({
                'code': 200,
                'msg': '修改成功',
                'data': {'id': course.id}
            })
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'}, status=400)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'修改失败，请稍后重试：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 PUT 请求'}, status=405)
