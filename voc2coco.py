import cv2
import json
from tqdm import tqdm
from glob import glob
import xmltodict
import argparse


def coco_format_init(classes):
    '''
        给 anno["categories"] 赋值
    '''
    anno_dict = {}
    anno_dict["licenses"] = [{"id":0, "name":"", "url":""}]
    anno_dict["info"] = {
        "contributor":"",
        "data_created":"",
        "description":"",
        "url":"",
        "version":"",
        "year":""
    }
    anno_dict["categories"] = []
    for i, name in enumerate(classes):
        anno_dict["categories"].append(
            {
                "supercategory": "_",
                "id": i,
                "name": name
            }
        )
    anno_dict["images"] = []
    anno_dict["annotations"] = []
    return anno_dict


def images_info_set(anno_dict, paths):
    '''
        给 anno_dict["images"] 赋值
    '''
    id = 0
    pbar = tqdm(total=len(paths))
    images_shapes = {}
    images_ids = {}
    for i, path in enumerate(paths):
        pbar.update(1)
        try:
            img = cv2.imread(path)
            h, w, c = img.shape
            imginfo = {}
            imginfo["coco_url"] = ""
            imginfo["data_captured"] = ""
            imginfo["file_name"] = path.split('/')[-1]
            imginfo["flickr_url"] = ""
            imginfo["license"] = 0
            imginfo["id"] = id
            images_ids[i] = id
            id += 1
            imginfo["height"] = h
            imginfo["width"] = w
        except Exception as e:
            print("{} is broke! ".format(path), e)
            continue
        anno_dict["images"].append(imginfo)
        images_shapes[i] = [h, w]
    return images_shapes, images_ids

def labels_info_set(anno_dict, paths, images_shapes, images_ids, classes):
    '''
        给 anno_dict["annotations"]赋值
    '''
    pbar = tqdm(total=len(paths))
    cls_map = {}
    for i, name in enumerate(classes):
        cls_map[name] = i
    print(cls_map)

    j = 0
    for i, path in enumerate(paths):
        pbar.update(1)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                xml_anno = xmltodict.parse(f.read())
            bboxes = []
            clses = []
            A = "annotation" if "annotation" in xml_anno else "Annotation"
            if "object" in xml_anno[A].keys():
                objs = xml_anno[A]["object"]
                if not isinstance(objs, list):
                    objs = [objs]
                for obj in objs:
                    if obj["name"] in classes:
                        bboxes.append([obj["bndbox"]["xmin"], obj["bndbox"]["ymin"], obj["bndbox"]["xmax"], obj["bndbox"]["ymax"]])
                        clses.append(cls_map[obj["name"]])
        except Exception as e:
            print(e)
            continue
        for x in range(len(bboxes)):
            try:
                bbox = [float(num) for num in bboxes[x]]
                bbox[2] = bbox[2] - bbox[0]
                bbox[3] = bbox[3] - bbox[1]
                seg = bbox[:2]
                seg.extend([bbox[0], bbox[1]+bbox[3]])
                seg.extend([bbox[0] + bbox[2], bbox[1] + bbox[3]])
                seg.extend([bbox[0] + bbox[2], bbox[1]])
                labelinfo = {}
                labelinfo["area"] = bbox[2] * bbox[3]
                labelinfo["bbox"] = bbox
                labelinfo["segmentation"] = [seg]
                labelinfo["image_id"] = images_ids[i]
                labelinfo["id"] = j
                j += 1
                labelinfo["iscrowd"] = 0
                labelinfo["category_id"] = int(clses[x])
            except Exception as e:
                print("label convert error! ", e)
                continue
            anno_dict["annotations"].append(labelinfo)


def main():
    parser = argparse.ArgumentParser(
        description='This script support converting voc format xmls to coco format json')
    parser.add_argument('--classes', type=list, default=["cloud", "person"])
    parser.add_argument('--img_dir', type=str, default="temp/*.jpg",
                        help='path to image files directory.')
    parser.add_argument('--output', type=str, default='output.json', help='path to output json file')
    args = parser.parse_args()

    anno_dict = coco_format_init(args.classes)
    print("ann_dict Init finised. class is {}".format(anno_dict["categories"]))
    image_paths = glob(args.img_dir)
    print(image_paths)
    label_paths = [p.replace(".jpg", ".xml") for p in image_paths]
    image_shapes, image_ids = images_info_set(anno_dict, image_paths)
    print(image_ids)
    print("ann_dict[images] generated.")
    labels_info_set(anno_dict, label_paths, image_shapes, image_ids, args.classes)
    print("ann_dict[annotation] generated.")

    with open(args.output, 'w') as f:
        json.dump(anno_dict, f, indent=4)

if __name__=="__main__":
    main()
    
    

