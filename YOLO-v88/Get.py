#yolov8 获取模型指标
from ultralytics import YOLO
 
model = YOLO("/root/YOLO-v88/runs/detect/YOLOv8s+ContextGuided+Wise-IoU_v3_9_yolodataset2/weights/best.pt")
metrics = model.val()  #在执行这一行的时候，系统会自动找你训练时候的yaml，若报错，看报错提示，需要将yaml放在对应位置
# 运行上面代码结束后，在下面其实已经给出了相应p、r、map
# 在路径下会有val文件夹，里面会有各种曲线图
print(metrics)  #查看metrics的所有存储内容
print("Precision:", metrics.box.p)
print("Recall:", metrics.box.r)
print("mAP@50:", metrics.box.map50)
print("mAP@50-95:", metrics.box.map)
print("Precision:", metrics.results_dict['metrics/precision(B)'])#获得更精确的值