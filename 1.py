# -*- coding = utf-8 -*-
from ultralytics import YOLO

# 使用 YOLO 类加载模型
model = YOLO("yolo/best.pt")

# 输出模型的详细信息（例如架构、层数、参数数量等）
model.info()

print(model.model)