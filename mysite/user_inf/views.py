import json
import os.path
import random
import time
import json
import re
import random
import time
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
import datetime
from django.conf import settings

from .models import User


def information(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        phone = data.get('tel', '').strip()
        passwd = data.get('passwd', '').strip()

        print(phone)

        if not phone or not passwd:
            return JsonResponse({'code': 400, 'msg': '手机号或密码不能为空'})

        try:
            user = User.objects.get(phone=phone)
            print(user.phone)
            print(user.username)
            print(user.gender)
            print(user.email)
            print(user.employeeId)
            print(user.address)
            print(user.registrationTime)
            print(user.rawpic)
            if check_password(passwd, user.password):
                try:
                    return JsonResponse({
                        'code': 200,
                        'msg': '登录成功',
                        'data': {
                            'username': user.username,  # 返回用户名
                            'phone': user.phone,  # 返回手机号
                            'gender': user.gender,  # 返回性别
                            'email': user.email,
                            'employeeId': user.employeeId,
                            'address': user.address,
                            'registrationTime': user.registrationTime,
                            'avatar': user.rawpic,
                        }
                    })
                except Exception as e:
                    print(e)
            else:
                return JsonResponse({'code': 401, 'msg': '密码错误'})

        except User.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '用户不存在'})

    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'})


def get_all(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        phone = data.get('phone', '').strip()
        print(phone)

        try:
            user = User.objects.get(phone=phone)
            print(user.phone)
            print(user.username)
            print(user.gender)
            print(user.email)
            print(user.employeeId)
            print(user.address)
            print(user.registrationTime)
            print(user.rawpic)
            try:
                return JsonResponse({
                    'code': 200,
                    'msg': '登录成功',
                    'data': {
                        'username': user.username,  # 返回用户名
                        'phone': user.phone,  # 返回手机号
                        'gender': user.gender,  # 返回性别
                        'email': user.email,
                        'employeeId': user.employeeId,
                        'address': user.address,
                        'registrationTime': user.registrationTime,
                        'avatar': user.rawpic,
                    }
                })
            except Exception as e:
                print(e)
        except User.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '用户不存在'})

    except Exception as e:
        print(e)
        return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'})


def user_updata(request):
    try:
        data = json.loads(request.body)
        avatar = data.get('avatar', '').strip()
        username = data.get('username', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        employeeId = data.get('employeeId', '').strip()
        address = data.get('address', '').strip()
        gender = data.get('gender', '').strip()
        print("avatar:", avatar)
        print("username:", username)
        print("phone:", phone)
        print("email:", email)
        print("employeeId:", employeeId)
        print("address:", address)
        print("gender:", gender)

        user = User.objects.get(phone=phone)
        user.gender = gender
        user.email = email
        user.phone = phone
        user.address = address
        user.employeeId = employeeId
        user.username = username
        user.rawpic = avatar
        user.save()
        return JsonResponse({'code': 200, 'msg': '修改成功', 'data': {'phone': phone}})
    except Exception as e:
        print(e)
        return JsonResponse({'code': 400, 'msg': 'JSON 格式错误'})


def send_code(request):
    """
    处理验证码发送请求
    前端传递：phone（手机号）
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        if not phone:
            return JsonResponse({'code': 400, 'msg': '请输入手机号'})

        # 生成6位数字验证码
        code = str(random.randint(100000, 999999))

        # 模拟发送短信验证码（实际可对接短信平台）
        print(f"发送验证码 {code} 到手机号 {phone}")

        # 将验证码保存到缓存中，有效期设置为300秒（5分钟）
        cache.set(f'verify_code_{phone}', code, 100)

        return JsonResponse({'code': 200, 'msg': '验证码已发送'})

    return JsonResponse({'code': 405, 'msg': '请求方法不允许'})


def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone', '').strip()
            code = data.get('code', '').strip()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            gender = data.get('gender', '').strip()

            # 校验必填字段
            if not all([phone, code, username, password, gender]):
                return JsonResponse({'code': 400, 'msg': '请填写完整信息'})

            # 验证手机号格式
            if not re.match(r'^1[3-9]\d{9}$', phone):
                return JsonResponse({'code': 400, 'msg': '手机号格式错误'})

            # 验证验证码
            cached_code = cache.get(f'verify_code_{phone}')
            if not cached_code or cached_code != code:
                cache.delete(f'verify_code_{phone}')
                return JsonResponse({'code': 400, 'msg': '验证码错误或已过期'})

            # 检查手机号是否已注册
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'code': 400, 'msg': '手机号已注册'})

            # 检查用户名是否重复
            if User.objects.filter(username=username).exists():
                return JsonResponse({'code': 400, 'msg': '用户名已存在'})

            # 验证密码长度
            if len(password) < 8 or len(password) > 20:
                return JsonResponse({'code': 400, 'msg': '密码需8-20位'})

            # 验证性别
            if gender not in ['男', '女']:
                return JsonResponse({'code': 400, 'msg': '性别无效'})

            now = timezone.now()
            time = now.replace(microsecond=0)

            # 创建用户
            User.objects.create(
                username=username,
                password=make_password(password),  # 手动加密密码
                phone=phone,
                gender=gender,
                registrationTime=time
            )

            cache.delete(f'verify_code_{phone}')
            return JsonResponse({'code': 200, 'msg': '注册成功'})

        except Exception as e:
            print(f'注册错误：{str(e)}')
            return JsonResponse({'code': 500, 'msg': '注册失败'})

    return JsonResponse({'code': 400, 'msg': '无效请求'})


def change_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            phone = data.get('phone', '').strip()
            code = data.get('code', '').strip()
            new_password = data.get('new_password', '').strip()

            if not phone or not code or not new_password:
                return JsonResponse({'code': 400, 'msg': '手机号、验证码或新密码不能为空'})

            if len(new_password) < 8 or len(new_password) > 20:
                return JsonResponse({'code': 400, 'msg': '密码长度需在 8~20 位之间'})

            cache_code = cache.get(f'verify_code_{phone}')
            if not cache_code or cache_code != code:
                return JsonResponse({'code': 401, 'msg': '验证码错误或已过期'})

            try:
                user = User.objects.get(phone=phone)

                user.password = make_password(new_password)
                user.save()

                cache.delete(f'verify_code_{phone}')

                return JsonResponse({'code': 200, 'msg': '密码修改成功'})
            except User.DoesNotExist:
                return JsonResponse({'code': 404, 'msg': '用户不存在'})

        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON 解析错误'})

    return JsonResponse({'code': 405, 'msg': '仅支持 POST 请求'})
