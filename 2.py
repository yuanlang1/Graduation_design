# -*- coding = utf-8 -*-
import torch

# 加载 checkpoint 文件（使用 map_location='cpu' 可避免 CUDA 相关问题）
checkpoint = torch.load("yolo/best.pt", map_location="cpu")

# 打印 checkpoint 中的所有键及其对应数据类型
for key, value in checkpoint.items():
    print(f"{key}: {type(value)}")
