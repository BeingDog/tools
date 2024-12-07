import cv2  
import numpy as np  
import glob
import os
import shutil
import random



def data2xyxy(parts, image, key="bbox"):
    h, w, c = image.shape
    if key == "bbox":
        class_id = int(parts[0])  
        x_center = float(parts[1]) * w  
        y_center = float(parts[2]) * h 
        width = float(parts[3]) * w 
        height = float(parts[4]) * h
        x_min = int(x_center - width / 2)  
        y_min = int(y_center - height / 2)  
        x_max = int(x_center + width / 2)  
        y_max = int(y_center + height / 2)
        return  x_min, y_min, x_max, y_max
    
    if key == "points":
        class_id = int(parts[0])
        p_list = np.array(parts[1:]).reshape((-1, 2))
        x_min, y_min = np.min(p_list, axis=0)
        x_max, y_max = np.max(p_list, axis=0)





# 类别标签列表（ID到名称的映射）  
classes = ['boat', 'humun', 'sup']  # 替换为你的类别名称
classes = ['Disposed Waste', 'Roll-Off Dumpster', 'Temporary Waste']
classes = ['Asphalt', 'Gravel', 'Sand', 'Temporary Soil']
classes = ['debris']
classes = ["swim", "drowm"]
# 设置颜色（BGR格式）  
colors = np.random.uniform(0, 255, size=(len(classes), 3))


path = "D:/dataset/drown/train/labels"
dst_path = "D:/dataset/drown/train/vis"
if not os.path.exists(dst_path):
    os.makedirs(dst_path)
txt_list = glob.glob(os.path.join(path, "*.txt"))
random.shuffle(txt_list)
n = len(txt_list)
train_txt_list = txt_list[:int(n*0.8)]
val_txt_list = [item for item in txt_list if item not in train_txt_list]

for annotation_file in txt_list:  
    image_file = annotation_file.replace("labels", "images").replace("txt","jpg")
    print(image_file)
    name = os.path.split(image_file)[-1]
    name_ = os.path.splitext(name)[0]
    # 读取标注文件  
    with open(annotation_file, 'r') as f:  
        annotations = f.readlines()

    # 保存标注文件
    # dst_train_dir = "D:/project/ultralytics/data/construction_rubbish/train"
    # if not os.path.exists(dst_train_dir):
    #     os.makedirs(dst_train_dir)
    # if annotation_file in train_txt_list:
    #     out_file = open(os.path.join(dst_train_dir, name_+".txt"), 'w')
    #     shutil.copy(image_file, os.path.join(dst_train_dir, name))
    # dst_val_dir = "D:/project/ultralytics/data/construction_rubbish/val"
    # if not os.path.exists(dst_val_dir):
    #     os.makedirs(dst_val_dir)
    # if annotation_file in val_txt_list:
    #     out_file = open(os.path.join(dst_val_dir, name_+".txt"), 'w')
    #     shutil.copy(image_file, os.path.join(dst_val_dir, name))

    # 加载图像  
    image = cv2.imread(image_file)
    h, w, c = image.shape  
    if image is None:  
        raise FileNotFoundError(f"Image file '{image_file}' not found.")  
    # 解析标注并绘制边界框  
    for annotation in annotations:  
        parts = annotation.strip().split()  
        if len(parts) == 5:  
            # 如果标注格式为：class_id x_center y_center width height 归一化值
            class_id = int(parts[0])  
            x_center = float(parts[1]) * w  
            y_center = float(parts[2]) * h 
            width = float(parts[3]) * w 
            height = float(parts[4]) * h   
            x_min = int(x_center - width / 2)  
            y_min = int(y_center - height / 2)  
            x_max = int(x_center + width / 2)  
            y_max = int(y_center + height / 2)  
        if len(parts) > 5:
            # 如果标志格式为 class_id , points
            parts = list(map(float, parts))
            class_id = int(parts[0])
            p_list = np.array(parts[1:]).reshape((-1, 2))
            x_min_n, y_min_n = np.min(p_list, axis=0)
            x_max_n, y_max_n = np.max(p_list, axis=0)
            x_min = w * x_min_n
            x_max = w * x_max_n
            y_min = h * y_min_n
            y_max = h * y_max_n

        # 确保边界框在图像范围内  
        x_min = int(max(0, x_min))  
        y_min = int(max(0, y_min))  
        x_max = int(min(image.shape[1], x_max))  
        y_max = int(min(image.shape[0], y_max))
        # if class_id == 0:
        #     out_file.write(str(3) + " " + " ".join([str(a) for a in [(x_min_n+x_max_n)/2, (y_min_n+y_max_n)/2, x_max_n-x_min_n, y_max_n-y_min_n]]) + '\n')

        # 绘制边界框
        color = [int(c) for c in colors[class_id]]
        cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), color, 2)    
        label = f"{classes[class_id]}"  
        cv2.putText(image, label, (int(x_min), int(y_min-2)),  
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)  
    
    cv2.imwrite(os.path.join(dst_path, name), image)
      