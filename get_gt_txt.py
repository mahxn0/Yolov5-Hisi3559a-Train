import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testPath', type=str, default='test/img', help='the path of test images')

    opt = parser.parse_args()
    # path_xml = './test/xml/'             # 测试集标签文件路径
    path_xml = os.path.join(os.path.dirname(opt.testPath), 'xml')
    path_img = os.listdir(opt.testPath)  # 测试集图片路径

    if not os.path.exists("./input"):
        os.makedirs("./input")
    if not os.path.exists("./input/ground-truth"):
        os.makedirs("./input/ground-truth")


    for image_id in tqdm(path_img):
        image_id = image_id.split('.')[0]
        with open("./input/ground-truth/" + image_id + ".txt", "w") as new_f:
            root = ET.parse(os.path.join(path_xml, (image_id + ".xml"))).getroot()
            for obj in root.findall('object'):
                if obj.find('difficult') != None:
                    difficult = obj.find('difficult').text
                    if int(difficult) == 1:
                        continue
                obj_name = obj.find('name').text
                bndbox = obj.find('bndbox')
                left = bndbox.find('xmin').text
                top = bndbox.find('ymin').text
                right = bndbox.find('xmax').text
                bottom = bndbox.find('ymax').text
                new_f.write("%s %s %s %s %s\n" % (obj_name, left, top, right, bottom))

    print("Conversion completed!")
