import glob

from django.http import JsonResponse
from django.conf import settings
import onnxruntime as ort
import torchvision.transforms as transforms
import cv2 as cv
import os
import numpy as np
from PIL import Image

# 导入FileSystemStorage
from django.core.files.storage import FileSystemStorage
import time
import random

from yolo import detect

img_size = 32
transformtest = transforms.Compose(
    [
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            # 均值和标准差
            mean=[0.4914, 0.4822, 0.4465],
            std=[0.2471, 0.2435, 0.2616],
        ),
    ]
)


def cv_imread(file_path):
    cv_img = cv.imdecode(np.fromfile(file_path, dtype=np.uint8), cv.IMREAD_COLOR)
    return cv_img


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=1, keepdims=True)


def imgclass(request):
    # 获取文件
    file = request.FILES.get("aiimg123456")
    # 检查文件是否存在
    if not file:
        return JsonResponse({"code": 400, "msg": "文件未上传"})
    # 使用 FileSystemStorage 保存图片
    fs = FileSystemStorage(location="static/ai")
    # 保证文件名不重复：会覆盖
    filename = f"{int(time.time() * 100)}_{random.randint(0, 999)}_{file.name}"
    fs.save(filename, file)
    # 响应访问地址到客户端
    img = settings.HOSTS_DOMAIN + f"/static/ai/{filename}"
    print(img)

    # AI 推理
    # 读取图片
    imgpath = os.path.join(os.path.dirname(__file__), "..", "static/ai", filename)
    print(imgpath)
    imgdata = cv_imread(imgpath)
    imgdata = cv.cvtColor(imgdata, cv.COLOR_BGR2RGB)
    # 将 numpy.ndarray 转换为 PIL.Image
    img_pil = Image.fromarray(imgdata)
    # 数据增强
    img_tensor = transformtest(img_pil)
    input_tensor = img_tensor.unsqueeze(0)  # 添加批量维度
    # 将图片转换为ONNX运行时所需的格式
    img_numpy = input_tensor.numpy()

    # 加载模型
    onnxPath = os.path.join(
        os.path.dirname(__file__),
        "..",
        "onnx",
        "yolov5s.onnx",
    )
    sess = ort.InferenceSession(onnxPath)
    # 运行onnx模型
    outputs = sess.run(None, {"input": img_numpy})
    output = outputs[0]

    # 应用softmax函数 将输出转为概率值
    probabilities = softmax(output)
    # 获取分类结果 取概率最大的索引值
    index = np.argmax(probabilities, axis=1)
    # 定义标签名，对应分类的结果
    lablename = "飞机、汽车、鸟类、猫、鹿、狗、青蛙、马、船、卡车".split("、")
    res = {"code": 200, "msg": "success", "url": img, "class": lablename[index[0]]}
    return JsonResponse(res)


def yolo(request):
    # 获取文件
    file = request.FILES.get("aiimg123456")
    # 检查文件是否存在
    if not file:
        return JsonResponse({"code": 400, "msg": "文件未上传"})
    # 使用 FileSystemStorage 保存图片
    fs = FileSystemStorage(location="static/yolo")
    # 保证文件名不重复：会覆盖
    filename = f"{int(time.time() * 100)}_{random.randint(0, 999)}_{file.name}"
    fs.save(filename, file)
    # 响应访问地址到客户端
    img = settings.HOSTS_DOMAIN + f"/static/yolo/{filename}"
    print(img)
    # 读取目录
    imgpath = os.path.join(os.path.dirname(__file__), "..", "static/yolo", filename)
    # 保存目录
    savepath = os.path.join(os.path.dirname(__file__), "..", "static")

    detect.run(
        weights="E:/django_project/yolo/runs/train/exp16/weights/best.pt",
        source=imgpath,  # 源文件
        save_txt=True,  # 保存txt
        project=savepath,  # 保存目录
        name="exp",  # 生成文件名
        exist_ok=True,
        device=0  # 运行GPU
    )
    # 读取与当前图片对应的检测结果 txt 文件
    labels_path = os.path.join(savepath, 'exp', 'labels')
    label_file = os.path.join(labels_path, f"{os.path.splitext(filename)[0]}.txt")  # 对应的 txt 文件

    category_counts = {'ripe': 0, 'unripe': 0, 'flower': 0, 'rotten': 0}

    # 检查是否存在与当前图片对应的 txt 文件
    if os.path.exists(label_file):
        with open(label_file, 'r') as f:
            for line in f:
                # 每行格式：class_id x_center y_center width height
                class_id = int(line.split()[0])  # 解析 class_id
                if class_id == 0:
                    category_counts['ripe'] += 1
                elif class_id == 1:
                    category_counts['unripe'] += 1
                elif class_id == 2:
                    category_counts['flower'] += 1
                elif class_id == 3:
                    category_counts['rotten'] += 1
    else:
        return JsonResponse({"code": 404, "msg": "检测结果未生成"})

    # 结果 URL
    exping = settings.HOSTS_DOMAIN + f"/static/exp/{filename}"

    # 返回 JSON 响应，包含图片 URL 和类别计数
    res = {
        "code": 200,
        "msg": "success",
        "url": img,
        "exp_url": exping,
        "category_counts": category_counts
    }

    print(category_counts)
    return JsonResponse(res)
