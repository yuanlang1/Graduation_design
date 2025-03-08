# views.py (位于 home 目录下)
import json
from django.http import JsonResponse
from django.utils import timezone
from home.models import TeacherInfo
import datetime
import os
from django.core.files.storage import FileSystemStorage
import random
from django.conf import settings


def teachers(request):
    """
    查询教师信息，支持按教师姓名、性别、职务、职称、教育程度、课程名称和年龄筛选。
    返回数据包括教师姓名、性别、职务、职称、教育程度、课程名称和年龄。
    """
    if request.method == 'GET':
        try:
            # 获取查询参数
            teacher_name = request.GET.get('teacherName', '').strip()
            teacher_gender = request.GET.get('teacherGender', '').strip()
            teacher_position = request.GET.get('teacherPosition', '').strip()
            teacher_title = request.GET.get('teacherTitle', '').strip()
            teacher_education = request.GET.get('teacherEducation', '').strip()
            course_name = request.GET.get('courseName', '').strip()
            teacher_age = request.GET.get('teacherAge', '').strip()

            # 查询 TeacherInfo 表作为主要数据源
            query = TeacherInfo.objects.all()

            # 按教师姓名筛选
            if teacher_name:
                query = query.filter(name__icontains=teacher_name)

            # 按性别筛选
            if teacher_gender:
                query = query.filter(gender__iexact=teacher_gender)

            # 按职务筛选
            if teacher_position:
                query = query.filter(post__icontains=teacher_position)

            # 按职称筛选
            if teacher_title:
                query = query.filter(title__icontains=teacher_title)

            # 按教育程度筛选
            if teacher_education:
                query = query.filter(education__icontains=teacher_education)

            # 按课程名称筛选
            if course_name:
                query = query.filter(course__icontains=course_name)

            # 按年龄筛选（转换为整数，如果有效）
            if teacher_age:
                try:
                    age = int(teacher_age)
                    query = query.filter(age=age)
                except ValueError:
                    return JsonResponse({'code': 400, 'msg': '年龄必须为数字'}, status=400)

            # 构造返回数据
            teacher_list = []
            for teacher in query:
                teacher_list.append({
                    'id': teacher.id,
                    'name': teacher.name or '',
                    'gender': teacher.gender or '',
                    'position': teacher.post or '',
                    'title': teacher.title or '',
                    'education': teacher.education or '',
                    'courseName': teacher.course or '',
                    'age': teacher.age if teacher.age is not None else ''
                })

            return JsonResponse({
                'code': 200,
                'data': teacher_list,
                'msg': '查询成功'
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'服务器错误，请稍后重试：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 GET 请求'}, status=405)


def Add_teachers(request):
    """
    添加教师信息，路径为 /Teacher_manage/Add_teachers/。
    """
    if request.method == 'POST':
        try:
            # 解析请求体中的 JSON 数据
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name', '').strip()
            gender = data.get('gender', '').strip()
            position = data.get('position', '').strip()
            title = data.get('title', '').strip()
            education = data.get('education', '').strip()
            course_name = data.get('courseName', '').strip()
            age = data.get('age', '').strip()

            # 验证必填字段（course 必须提供）
            if not course_name:
                return JsonResponse({'code': 400, 'msg': '课程名称不能为空'}, status=400)
            if not name:
                return JsonResponse({'code': 400, 'msg': '教师姓名不能为空'}, status=400)

            # 验证年龄（转换为整数，如果提供）
            if age:
                try:
                    age = int(age)
                    if age <= 0:
                        return JsonResponse({'code': 400, 'msg': '年龄必须为正整数'}, status=400)
                except ValueError:
                    return JsonResponse({'code': 400, 'msg': '年龄必须为数字'}, status=400)
            else:
                age = None  # 如果年龄为空，设置为 None

            # 验证性别（可选，限制为 "男" 或 "女"）
            if gender and gender not in ['男', '女']:
                return JsonResponse({'code': 400, 'msg': '性别必须为“男”或“女”'}, status=400)

            print(1)
            # 创建 TeacherInfo 实例
            teacher = TeacherInfo(
                name=name,
                gender=gender,
                course=course_name,
                post=position,
                title=title,
                age=age,
                education=education
            )
            print(2)
            try:
                teacher.save()
                print("保存成功")
            except Exception as e:
                print("保存失败:", e)
            print(3)
            return JsonResponse({
                'code': 200,
                'msg': '添加成功',
                'data': {'id': teacher.id}
            })
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'}, status=400)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'服务器错误，请稍后重试：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 POST 请求'}, status=405)


def Delete_teachers(request, id):
    """
    删除指定教师（通过 id），路径为 /Teacher_manage/Delete_teachers/<id>/。
    """
    if request.method == 'DELETE':
        try:
            # 查询并删除 TeacherInfo 记录
            teacher = TeacherInfo.objects.get(id=id)
            teacher.delete()

            return JsonResponse({
                'code': 200,
                'msg': '删除成功'
            })
        except TeacherInfo.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '教师不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '删除失败，请稍后重试'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 DELETE 请求'}, status=405)


# home/views.py
def Update_teachers(request, id):
    """
    修改指定教师信息（通过 id），路径为 /Teacher_manage/teachers/<id>/。
    """
    if request.method == 'PUT':
        try:
            try:
                # 查询 TeacherInfo 记录
                teacher = TeacherInfo.objects.get(id=id)
                # 解析请求体中的 JSON 数据
                data = json.loads(request.body.decode('utf-8'))
                name = data.get('name', '').strip()
                gender = data.get('gender', '').strip()
                position = data.get('position', '').strip()
                title = data.get('title', '').strip()
                education = data.get('education', '').strip()
                course_name = data.get('courseName', '').strip()
                age = data.get('age', '')
            except Exception as e:
                print(e)

            print(1)

            # 验证必填字段（course 必须提供）
            if not course_name:
                return JsonResponse({'code': 400, 'msg': '课程名称不能为空'}, status=400)
            if not name:
                return JsonResponse({'code': 400, 'msg': '教师姓名不能为空'}, status=400)

            print(2)
            # 验证年龄（转换为整数，如果提供）
            if age:
                try:
                    age = int(age)
                    if age <= 0:
                        return JsonResponse({'code': 400, 'msg': '年龄必须为正整数'}, status=400)
                except ValueError:
                    return JsonResponse({'code': 400, 'msg': '年龄必须为数字'}, status=400)
            else:
                age = None  # 如果年龄为空，设置为 None

            print(3)
            # 验证性别（可选，限制为 "男" 或 "女"）
            if gender and gender not in ['男', '女']:
                return JsonResponse({'code': 400, 'msg': '性别必须为“男”或“女”'}, status=400)
            print(4)
            # 更新 TeacherInfo 实例
            teacher.name = name
            teacher.gender = gender
            teacher.course = course_name
            teacher.post = position
            teacher.title = title
            teacher.age = age
            teacher.education = education
            teacher.save()
            print(5)
            return JsonResponse({
                'code': 200,
                'msg': '修改成功',
                'data': {'id': teacher.id}
            })
        except TeacherInfo.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '教师不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'}, status=400)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'服务器错误，请稍后重试：{str(e)}'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 PUT 请求'}, status=405)
