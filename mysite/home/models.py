from django.db import models


class TeacherInfo(models.Model):
    """
    用于存储教师信息的模型，包括教师基本信息、课程、职务、职称等。
    """
    id = models.AutoField(primary_key=True, verbose_name="序号")
    name = models.CharField(max_length=30, null=False, blank=True, verbose_name="教师姓名")
    gender = models.CharField(max_length=2, null=False, blank=True, verbose_name="性别")
    course = models.CharField(max_length=20, null=False, blank=True, verbose_name="课程名称")
    post = models.CharField(max_length=20, null=False, blank=True, verbose_name="职务")
    title = models.CharField(max_length=20, null=False, blank=True, verbose_name="职称")
    age = models.IntegerField(null=False, blank=True, verbose_name="年龄")
    education = models.CharField(max_length=255, null=False, blank=True, verbose_name="教育程度")

    class Meta:
        verbose_name = "教师信息"
        verbose_name_plural = "教师信息"

    def __str__(self):
        return f"教师 {self.name}"


class CourseInfo(models.Model):
    """
    用于存储课程信息的模型，包括课程编号和课程名称。
    """
    id = models.AutoField(primary_key=True, verbose_name="序号")
    course_name = models.CharField(max_length=255, null=False, blank=True, verbose_name="课程名称")
    class_name = models.CharField(max_length=30, null=False, blank=True, verbose_name="课堂名称")
    teacher_name = models.CharField(max_length=20, null=False, blank=True, verbose_name="授课教师")
    location = models.CharField(max_length=255, null=False, blank=True, verbose_name="上课地址")
    stage = models.IntegerField(null=False, blank=True, verbose_name="节数")
    course_time = models.DateTimeField(null=False, blank=True, verbose_name="上课时间")

    class Meta:
        verbose_name = "课程信息"
        verbose_name_plural = "课程信息"

    def __str__(self):
        return f"课程 {self.course_name}"


class ClassroomStatus(models.Model):
    """
    用于存储课堂状态和专注度数据的模型，包括课堂信息、教师和专注度指标。
    """
    course_id = models.IntegerField(primary_key=True, verbose_name="课程号")
    # id = models.AutoField(primary_key=True, verbose_name="序号")
    # class_name = models.CharField(max_length=30, null=False, blank=True, verbose_name="课堂名称")
    # course_name = models.CharField(max_length=255, null=False, blank=True, verbose_name="课程名称")
    # teacher_name = models.CharField(max_length=20, null=False, blank=True, verbose_name="授课教师")
    estimate = models.CharField(max_length=20, null=False, blank=True, verbose_name="专注度评估")
    dtime = models.DateTimeField(null=False, blank=True, verbose_name="评价时间")

    class Meta:
        verbose_name = "课堂状态"
        verbose_name_plural = "课堂状态"

    def __str__(self):
        return f" {self.course_id} - {self.estimate} - {self.dtime}"


class RecognitionResult(models.Model):
    """
    用于存储课堂识别结果信息的模型，包括课堂信息、学生行为、专注度评估和图片路径。
    """
    id = models.AutoField(primary_key=True, verbose_name="序号")
    class_id = models.IntegerField(null=False, blank=True, verbose_name="课堂号")
    # class_name = models.CharField(max_length=30, null=False, blank=True, verbose_name="课堂名称")
    # course_name = models.CharField(max_length=255, null=False, blank=True, verbose_name="课程名称")
    estimate = models.CharField(max_length=20, null=False, blank=True, verbose_name="专注度评估")
    dtime = models.DateTimeField(null=False, blank=False, verbose_name="评价时间")
    rawpic = models.CharField(max_length=255, null=False, blank=True, verbose_name="原始数据")
    resultpic = models.CharField(max_length=255, null=False, blank=True,
                                 verbose_name="识别结果数据")
    result = models.CharField(max_length=255, null=True, blank=True,
                                 verbose_name="识别数据")

    class Meta:
        verbose_name = "识别结果信息"
        verbose_name_plural = "识别结果信息"

    def __str__(self):
        return f"课堂 {self.class_name} - 时间：{self.dtime}"
