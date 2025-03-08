# views.py
from django.http import JsonResponse
from django.utils import timezone
from .models import CourseInfo, TeacherInfo, ClassroomStatus, RecognitionResult
import datetime


def top_stats(request):
    """
    获取顶部统计数据：全校班级数、正在上课班级数和当前课堂专注度。
    """
    if request.method == 'GET':
        try:
            # 1. 获取全校班级数（唯一 `class_name` 的数量）
            total_classes = ClassroomStatus.objects.values('class_name').distinct().count()

            # 2. 获取正在上课的班级数
            # 假设 "正在上课" 定义为 `dtime` 在当前时间 ± 1 小时内
            current_time = timezone.now()
            time_threshold = datetime.timedelta(hours=1)
            active_classes = ClassroomStatus.objects.filter(
                dtime__gte=current_time - time_threshold,
                dtime__lte=current_time + time_threshold
            ).values('class_name').distinct().count()

            # 3. 获取当前课堂专注度（取最近一条记录的 `estimate` 值）
            # 优先从 RecognitionResult 获取，如果没有则使用 ClassroomStatus
            latest_status = ClassroomStatus.objects.select_related('teacher').order_by('-dtime').first()
            if latest_status:
                recognition = RecognitionResult.objects.filter(classroom_statuses=latest_status).first()
                focus_level = (recognition.estimate if recognition and recognition.estimate else
                               latest_status.estimate) if latest_status.estimate else '无'
            else:
                focus_level = '无'

            # 构造响应数据
            data = {
                'code': 200,
                'data': {
                    'totalClasses': total_classes,
                    'activeClasses': active_classes,
                    'focusLevel': focus_level,
                }
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '服务器错误，请稍后重试'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 GET 请求'}, status=405)


def chart_data(request):
    """
    获取年级课堂专注度图表数据。
    """
    if request.method == 'GET':
        try:
            # 假设从 ClassroomStatus 表中按年级统计专注度
            grades = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级']
            focus_levels = []

            for grade in grades:
                # 假设通过 class_name 提取年级，并计算平均专注度
                status_list = ClassroomStatus.objects.filter(class_name__startswith=grade)
                if status_list.exists():
                    # 优先从 RecognitionResult 获取 estimate，如果没有则使用 ClassroomStatus
                    estimates = []
                    for status in status_list:
                        recognition = RecognitionResult.objects.filter(classroom_statuses=status).first()
                        estimate = (recognition.estimate if recognition and recognition.estimate else
                                    status.estimate) or '0.5'
                        estimates.append(float(estimate) if estimate.isdigit() else 0.5)
                    avg_focus = sum(estimates) / len(estimates) if estimates else 0.5
                    focus_levels.append(avg_focus)
                else:
                    focus_levels.append(0.5)  # 默认值

            data = {
                'code': 200,
                'data': {
                    'categories': grades,
                    'series': [{
                        'name': '年级专注度',
                        'data': focus_levels,
                        'color': '#1E90FF',
                    }],
                }
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '服务器错误，请稍后重试'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 GET 请求'}, status=405)


def top10_classes(request):
    """
    获取上堂课课堂专注度前10名班级。
    """
    if request.method == 'GET':
        try:
            # 假设从 ClassroomStatus 表中按最近的 dtime 排序，并按 estimate 降序取前10
            current_time = timezone.now()
            time_threshold = datetime.timedelta(hours=2)  # 假设最近两小时的上课记录
            top_classes = ClassroomStatus.objects.select_related('teacher').filter(
                dtime__gte=current_time - time_threshold
            ).order_by('-estimate')[:10]

            data = {
                'code': 200,
                'data': [
                    {
                        'className': status.class_name,
                        'teacher': status.teacher.name if status.teacher else status.teacher_name or '未知教师',
                        'score': (float(status.estimate) if status.estimate and status.estimate.isdigit() else 0.0),
                    }
                    for status in top_classes
                ]
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '服务器错误，请稍后重试'}, status=500)
    return JsonResponse({'code': 405, 'msg': '仅支持 GET 请求'}, status=405)
