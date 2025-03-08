from ultralytics import YOLO


model = YOLO('/root/YOLO-v88/model/yolov8s.yaml')

# 训练模型
results = model.train(
    data='datasets/data4/dataset.yaml',
    epochs=200,
    batch=32,
    imgsz=640,
    name='YOLOv8s+ContextGuided_7'
)
