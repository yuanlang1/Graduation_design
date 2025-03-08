from ultralytics import YOLO


model = YOLO('yolov8s.yaml')

# 训练模型
results = model.train(
    data='datasets/yolo_dataset/data.yaml',
    epochs=200,
    batch=32,
    imgsz=640,
    name='yolov8s_6'
)
