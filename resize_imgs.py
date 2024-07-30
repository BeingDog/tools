import json  
from PIL import Image  
  
def resize_image_and_annotations(image_path, json_path, output_image_path, output_json_path, target_size):  
    # 读取原始图像并调整大小  
    original_image = Image.open(image_path)  
    width, height = original_image.size  
    resized_image = original_image.resize(target_size)  
    resized_image.save(output_image_path)  
  
    # 读取标注文件  
    with open(json_path, 'r') as json_file:  
        data = json.load(json_file)  
  
    # 计算缩放比例  
    scale_x = target_size[0] / width  
    scale_y = target_size[1] / height  
  
    # 调整标注中的点和尺寸  
    for shape in data['shapes']:  
        shape['points'] = [(int(round(x * scale_x)), int(round(y * scale_y))) for x, y in shape['points']]  
        if 'rectangle' in shape['shape_type']:  
            shape['width'] *= scale_x  
            shape['height'] *= scale_y  
            # 如果需要，调整x和y位置以匹配新尺寸的左上角  
            # shape['points'][0][0] = ...  
            # shape['points'][0][1] = ...  
  
    # 保存调整后的标注到新的json文件  
    with open(output_json_path, 'w') as json_file:  
        json.dump(data, json_file, ensure_ascii=False, indent=2)  
  
# 使用函数  
image_path = 'path_to_your_image.jpg'  
json_path = 'path_to_your_labelme_annotations.json'  
output_image_path = 'resized_image.jpg'  
output_json_path = 'resized_annotations.json'  
target_size = (800, 600)  # 指定的新尺寸  
  
resize_image_and_annotations(image_path, json_path, output_image_path, output_json_path, target_size)