import cv2
import torch
from ultralytics import YOLO

# 1. 加载训练好的 YOLOv8 模型
model = YOLO("mysite/yolo/best.pt")

# 2. 读取课堂图片
image_path = "0.jpg"  # 替换为你的图片路径
image = cv2.imread(image_path)

# 3. 运行 YOLOv8 进行检测
results = model(image)

# 4. 解析检测结果并绘制框
for box in results[0].boxes.xyxy:
    x1, y1, x2, y2 = map(int, box[:4])  # 获取边界框坐标
    class_id = int(results[0].boxes.cls[0])  # 识别的类别ID
    class_name = model.names[class_id]  # 获取类别名称

    # 画框
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# 5. 保存并显示检测结果
output_path = "classroom_detected.jpg"
cv2.imwrite(output_path, image)
cv2.imshow("Detected Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
