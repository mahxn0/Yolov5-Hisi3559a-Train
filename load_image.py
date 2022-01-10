import os
import urllib.request
import xml.etree.ElementTree as ET
import yaml
from PIL import Image

# 下载单个txt
def load_image(urlPath, data_yaml):

    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data/images'):
       os.mkdir('data/images')
    if not os.path.exists('data/images/train'):
       os.mkdir('data/images/train')
    if not os.path.exists('data/images/val'):
       os.mkdir('data/images/val')
    if not os.path.exists('data/images/test'):
       os.mkdir('data/images/test')
    if not os.path.exists('data/labels'):
       os.mkdir('data/labels')
    if not os.path.exists('data/labels/train'):
       os.mkdir('data/labels/train')
    if not os.path.exists('data/labels/val'):
       os.mkdir('data/labels/val')
    if not os.path.exists('data/labels/test'):
       os.mkdir('data/labels/test')
    if not os.path.exists('data/Annatations'):
       os.mkdir('data/Annatations')

    train_file = open('./train.txt', 'w')
    val_file = open('./val.txt', 'w')
    test_file = open('./test.txt', 'w')
    urls = open(urlPath)
    num_pic = int(len(urls.readlines()) * 0.5)
    count = 0
    trainval = 0.9
    train = 0.9
    keep_1 = int(trainval * train * num_pic)   # 训练集
    keep_2 = int(trainval * num_pic)    # 训练集 验证集
    for url in open(urlPath):
        fileName = url.split('/')[-1]
        fileName = fileName.split('?')[0]
        savePath = ''
        if '.jpg' in fileName or '.png' in fileName:

            if count < keep_1:
                savePath = 'data/images/train/' + fileName
                path_train = str(os.path.join(os.getcwd(), '/data/images/train/', fileName))
                train_file.write(path_train + '\n')

            elif count < keep_2:
                savePath = 'data/images/val/' + fileName
                path_val = str(os.path.join(os.getcwd(), '/data/images/val/', fileName))
                val_file.write(path_val + '\n')

            else:
                savePath = 'data/images/test/' + fileName
                path_test = str(os.path.join(os.getcwd(), '/data/images/test/', fileName))
                test_file.write(path_test + '\n')

            count += 1
        elif 'xml' in fileName:
            savePath = 'data/Annatations/' + fileName
        print("Load file: ", fileName)
        urllib.request.urlretrieve(url, savePath)
    train_file.close()
    val_file.close()
    test_file.close()
    labels(data_yaml)

# 下载文件夹所有的txt
def load_train_image(urlPath, data_yaml):
    imgUrlTxts = os.listdir(urlPath)
    for imgUrlTxt in imgUrlTxts:
        if imgUrlTxt.split('.')[1] != 'txt':
            continue
        load_image(os.path.join(urlPath, imgUrlTxt), data_yaml)

def load_test_image(urlPath, source_path):

    for url in open(urlPath):
        if not os.path.exists(source_path):
            os.makedirs(source_path)
        xml_path = os.path.join(os.path.dirname(source_path), 'xml')
        if not os.path.exists(xml_path):
            os.mkdir(xml_path)
        fileName = url.split('/')[-1]
        fileName = fileName.split('?')[0]
        savePath = ''
        if '.jpg' in fileName or '.png' in fileName:
            savePath = os.path.join(source_path, fileName)
        elif 'xml' in fileName:
            savePath = os.path.join(xml_path, fileName)
        print("Load file: ", fileName)
        urllib.request.urlretrieve(url, savePath)        


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def labels(data_yaml):
    with open(data_yaml) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    classes = data['names']
    print(classes)

    sets = ['train', 'val', 'test']

    for image_set in sets:
        image_ids = open('./%s.txt' % (image_set)).read().strip().split()
        for image_id in image_ids:
            image_path = image_id.split('.')[0].split('/')[-1]
            img_path = os.path.join('./data/images', image_set, (image_path + '.jpg'))
            xml_path = os.path.join('./data/Annatations/', (image_path + '.xml'))
            in_file = open(xml_path)
            out_file = open('./data/labels/%s/%s.txt' % (image_set, image_path), 'w')
            tree = ET.parse(in_file)
            root = tree.getroot()
            size = root.find('size')
            w = int(size.find('width').text)
            h = int(size.find('height').text)

            for obj in root.iter('object'):
                difficult = obj.find('difficult').text
                cls = obj.find('name').text
                if cls not in classes or int(difficult) == 1:
                    continue
                cls_id = classes.index(cls)
                xmlbox = obj.find('bndbox')
                b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
                     float(xmlbox.find('ymax').text))
                if w == 0 or h == 0:
                    img = Image.open(img_path)
                    w, h = img.size[0], img.size[1]
                bb = convert((w, h), b)
                out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')



if __name__ == ('__main__'):
    load_all_image('./urlTxtPath', './data/ab.yaml')
