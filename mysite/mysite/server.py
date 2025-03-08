# -*- coding = utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render


def server(request):
    print(request)
    print("当前发生请求方式:", request.method)
    print("当前提交的数据:", request.POST)
    if request.method == "POST":
        username = request.POST.get('username')
        return HttpResponse('POST请求，用户名：%s' % username)
    else:
        username = request.GET.get('username')
        return HttpResponse('GET请求，用户名：%s' % username)


def index(request):
    s = '111'
    i = 10
    list1 = ['a', 'b']
    dic = {"name": 'aa', "age": 10}

    def say():
        return "hello world"

    return render(request, "index.html", locals())
