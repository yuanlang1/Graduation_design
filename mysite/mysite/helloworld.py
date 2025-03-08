# -*- coding = utf-8 -*-
from django.http import HttpResponse, QueryDict


def index(request, n):
    return HttpResponse('这是第%d页' % n)
