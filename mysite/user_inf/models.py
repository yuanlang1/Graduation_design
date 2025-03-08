from django.db import models


class User(models.Model):
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]

    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    username = models.CharField(max_length=50, null=False, blank=True, default="默认用户名", verbose_name="账号")
    password = models.CharField(max_length=128, null=False, blank=True, verbose_name="密码")
    gender = models.CharField(max_length=10, null=False, blank=True, choices=GENDER_CHOICES, default="男")
    email = models.CharField(max_length=128, null=False, blank=True, verbose_name="邮箱", default="未设置")
    employeeId = models.CharField(max_length=128, null=False, blank=True, verbose_name="职工号", default="未设置")
    address = models.CharField(max_length=128, null=False, blank=True, verbose_name="地址", default="未设置")
    registrationTime = models.DateTimeField(null=False, blank=True, verbose_name="注册时间")
    rawpic = models.CharField(max_length=255, null=False, blank=True, verbose_name="头像", default='/default.jpg')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"


