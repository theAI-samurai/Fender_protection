import cv2
from os.path import dirname, realpath
import os
import numpy as np

dir_of_file = dirname(realpath(__file__))
os.chdir(dir_of_file)
print(dir_of_file)


class ObjDetect:

    def __init__(self, cfgPath, wgtPath, dataPath):
        self.cfg = cfgPath
        self.weight = wgtPath
        self.classes = dataPath
        self.colors = np.random.randint(0, 255, size=(200, 3), dtype="uint8")

    def load_network(self):
        net_ = cv2.dnn.readNetFromDarknet(self.cfg, self.weight)
        return net_


ship = ObjDetect(dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                 dir_of_file + '/ship/cfg/yolov3_full_ship_2000.weights',
                 dir_of_file + '/ship/cfg/ship.data')

frame = r'D:\cloned_repos\darknet_test\ship\test_data\001.jpg'
frame_img = cv2.imread(frame)


blob = cv2.dnn.blobFromImage(frame_img, scalefactor=1.0, size=(416, 416), mean=(0, 0, 0), swapRB=True, crop=False)
print("blob: shape {}".format(blob.shape))
net = ship.load_network()
net.setInput(blob)
outs = net.forward()  # numpy array
len(outs)

boxes = []
confidences = []
class_ids = []

height, width = frame_img.shape[:2]
with open(ObjDetect.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]
for detection in outs:
    scores = detection[5:]
    class_id = np.argmax(scores)
    confidence = scores[class_id]
    if confidence > 0.3:
        center_x = int(detection[0] * width)
        center_y = int(detection[1] * height)
        w = int(detection[2] * width)
        h = int(detection[3] * height)
        x = center_x - w / 2
        y = center_y - h / 2
        boxes.append([x, y, w, h])
        confidences.append(float(confidence))
        class_ids.append(class_id)

ObjDetect.cl


