from ultralytics import YOLO


model = YOLO('yolov8.yaml')

# 训练模型
results = model.train(
    data='datasets/data/dataset.yaml',
    epochs=200,
    batch=32,
    imgsz=640,
    name='YOLOv8s_Wise-IoU_v3'
)
