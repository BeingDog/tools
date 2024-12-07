import os
import glob
import cv2
import shutil
import xml.etree.ElementTree as ET

def convert_yolo_to_xml(yolo_file, image_name, shape, output_dir, classes):
    # Parse YOLO format
    with open(yolo_file, 'r') as f:
        lines = f.readlines()
    
    # Create XML root
    annotation = ET.Element('annotation')
    folder = ET.SubElement(annotation, 'folder').text = 'images'  # Adjust as needed
    filename = ET.SubElement(annotation, 'filename').text = image_name
    path = ET.SubElement(annotation, 'path').text = os.path.join(output_dir, image_name)
    
    # Assume image size is known and constant for simplicity (or load from another file)
    source = ET.SubElement(annotation, 'source')
    ET.SubElement(source, 'database').text = 'Unknown'
    
    size = ET.SubElement(annotation, 'size')
    h, w, c = shape
    ET.SubElement(size, 'width').text = str(w)  # Example width
    ET.SubElement(size, 'height').text = str(h)  # Example height
    ET.SubElement(size, 'depth').text = str(c)  # Number of channels (RGB)
    
    segmented = ET.SubElement(annotation, 'segmented').text = '0'
    
    # Parse each object in YOLO format
    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        class_name = classes[class_id]
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        
        obj = ET.SubElement(annotation, 'object')
        ET.SubElement(obj, 'name').text = class_name
        ET.SubElement(obj, 'pose').text = 'Unspecified'
        ET.SubElement(obj, 'truncated').text = '0'
        ET.SubElement(obj, 'difficult').text = '0'
        
        bndbox = ET.SubElement(obj, 'bndbox')
        
        # Convert YOLO format to Pascal VOC format
        img_width = w  # Example width
        img_height = h  # Example height
        
        xmin = int((x_center - width / 2) * img_width)
        ymin = int((y_center - height / 2) * img_height)
        xmax = int((x_center + width / 2) * img_width)
        ymax = int((y_center + height / 2) * img_height)
        
        ET.SubElement(bndbox, 'xmin').text = str(xmin)
        ET.SubElement(bndbox, 'ymin').text = str(ymin)
        ET.SubElement(bndbox, 'xmax').text = str(xmax)
        ET.SubElement(bndbox, 'ymax').text = str(ymax)
    
    # Write XML to file
    xml_tree = ET.ElementTree(annotation)
    xml_filename = os.path.join(output_dir, os.path.splitext(image_name)[0] + '.xml')
    xml_tree.write(xml_filename, encoding='utf-8', xml_declaration=True)
    print(f'Saved {xml_filename}')

# Example usage
path = "D:/project/ultralytics/data/construction_rubbish/det/images/val"
jpg_paths = glob.glob(os.path.join(path, "*.jpg"))
for index, jpg in enumerate(jpg_paths):
    print(index, jpg)
    yolo_file = jpg.replace("images", "labels").replace(".jpg", ".txt")
    image_name = os.path.split(jpg)[-1]
    h, w, c = cv2.imread(jpg).shape
    output_dir = "D:/dataset/tinktek_person_data/construction_rubbish"
    os.makedirs(output_dir, exist_ok=True)
    classes = ['construction rubbish', 'construction rubbish', "construction rubbish", "construction rubbish"]  # List of class names in the same order as in YOLO file
    shutil.copy(jpg, os.path.join(output_dir, image_name))
    if not os.path.exists(yolo_file):
        print("不存在对应txt")
        continue
    convert_yolo_to_xml(yolo_file, image_name, (h,w,c), output_dir, classes)