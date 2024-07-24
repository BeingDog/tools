import os
import json
import glob
import shutil
from tqdm import tqdm  
import argparse 
import xml.etree.ElementTree as ET
from PIL import Image  


def indent(elem, level=0):
    '''
    美化xml的缩进排版
    '''
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i



def labelme_json_to_pascal_voc(json_filepath, xml_filepath, resize=None):  
    # 加载 JSON 文件
    with open(json_filepath, 'r') as f:  
        data = json.load(f)  
    # 创建 XML 根元素  
    root = ET.Element("annotation")  
  
    # 添加文件夹、文件名、来源等（可选）  
    folder = ET.SubElement(root, "folder").text = "images"  
    filename = ET.SubElement(root, "filename").text = data['imagePath'].split('/')[-1]
    path = ET.SubElement(root, "path").text = os.path.join(folder, filename)
    source = ET.SubElement(root, "source")  
    ET.SubElement(source, "database").text = "Unknown"  
  
    # 添加图像尺寸  
    size = ET.SubElement(root, "size")  
    ET.SubElement(size, "width").text = str(data['imageWidth'])  
    ET.SubElement(size, "height").text = str(data['imageHeight'])  
    ET.SubElement(size, "depth").text = "3"

    # 添加segmented
    segmented = ET.SubElement(root, "segmented").text = "0"

    # 添加标注的对象  
    for shape in data['shapes']:  
        obj = ET.SubElement(root, "object")  
        ET.SubElement(obj, "name").text = shape['label']
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"

        bndbox = ET.SubElement(obj, "bndbox")  
  
        # 注意：这里需要转换多边形为边界框（简单处理）  
        # 或者，可以保留多边形，但 PASCAL VOC 通常用于边界框  
        xmin = min(point[0] for point in shape['points'])  
        ymin = min(point[1] for point in shape['points'])  
        xmax = max(point[0] for point in shape['points'])  
        ymax = max(point[1] for point in shape['points'])

        if resize:
            src_w = data['imageWidth']
            src_h = data['imageHeight']
            dst_w, dst_h = resize
            xmin = dst_w * xmin / src_w
            ymin = dst_h * ymin / src_h
            xmax = dst_w * xmax / src_w
            ymax = dst_h * ymax / src_h
  
        ET.SubElement(bndbox, "xmin").text = str(int(xmin))  
        ET.SubElement(bndbox, "ymin").text = str(int(ymin))  
        ET.SubElement(bndbox, "xmax").text = str(int(xmax))  
        ET.SubElement(bndbox, "ymax").text = str(int(ymax))  
  
    # 写入 XML 文件  
    indent(root)  # 执行美化方法
    tree = ET.ElementTree(root)
    tree.write(xml_filepath, encoding='utf-8', xml_declaration=True)    
  
 

def jsondir2vocdir(src_dir, dst_dir, copy=True, resize=None):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for json_path in tqdm(glob.glob(src_dir)):
        img_path = json_path.replace("json", "jpg")
        if copy:
            filename = os.path.split(img_path)[-1]
            if resize:
                image = Image.open(img_path)  
                resized_image = image.resize(resize)
                resized_image.save(os.path.join(dst_dir, filename)) 
            else:
                shutil.copy(img_path, os.path.join(dst_dir, filename))
        jsonname = os.path.splitext(os.path.split(json_path)[-1])[0]
        xml_path = os.path.join(dst_dir, jsonname+".xml")
        labelme_json_to_pascal_voc(json_path, xml_path, resize=resize)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='convert labelme to labelImg.')  
    parser.add_argument('--json_dir', type=str, default="test_labelme/*.json", help='json文件夹路径')
    parser.add_argument('--xml_dir', type=str, default="temp/", help='需要保存的xml文件夹路径')  
    parser.add_argument('--copy', type=bool, default=True, help='是否把图像copy到新的文件夹，与保存的xml文件同个文件夹')
    parser.add_argument('--resize', default=(1920, 1080), help="是否在copy时把图像resize到指定尺寸, 标注文件也等比缩放")  
    
    # 解析命令行参数  
    args = parser.parse_args()
    print(args)
    jsondir2vocdir(args.json_dir, args.xml_dir, copy=args.copy, resize=args.resize)