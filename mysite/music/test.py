# -*- coding = utf-8 -*-
from django.http import HttpResponse, QueryDict
from django.shortcuts import render


def index(request):
    s = '111'
    i = 10
    list1 = ['a', 'b']
    dic = {"name": 'aa', "age": 10}

    def say():
        return "hello world"

    return render(request, "index.html", locals())
