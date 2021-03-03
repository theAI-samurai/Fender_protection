from darknet import *
import cv2
from os.path import dirname, realpath
import os
import requests

dir_of_file = dirname(realpath(__file__))
os.chdir(dir_of_file)

USING_VIDEO_FILE = True
READ_FRAMES = True
INPUT_WIDTH = 960
INPUT_HEIGHT = 576
POST_LINK = 'http://vmi317167.contaboserver.net/ship-detection-api/api/v1/notification/create'

fender_path = dir_of_file + '/fender.jpg'

IP_STREAM_1 = 'ws://localhost:8082/'
IP_STREAM_1 = 'D:/00000000073000000.mp4'


ship_det = ObjectDetection(dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                         dir_of_file + '/ship/cfg/yolov3_full_ship_2000.weights',
                         dir_of_file + '/ship/cfg/ship.data'
                         )
from PIL import Image
url = 'http://vmi317167.contaboserver.net/ship-detection-api/api/v1/guard/drawing/2'
img = Image.open(requests.get(url, stream=True).raw).convert('RGB')
#img.show()
img.save('fender.jpg')
#cv2.imshow('test', img)

def fender_coordi(path_):
    fender_ref = cv2.imread(path_)  # ---> H=400, W=500
    print(fender_ref.shape)
    #fender_ref = cv2.resize(fender_ref, (INPUT_WIDTH, INPUT_HEIGHT), interpolation=cv2.INTER_AREA)  # ---> H=576, W=960
    lst_x = []
    lst_y = []
    for i in range(fender_ref.shape[0]):  # ----> Height
        for j in range(fender_ref.shape[1]):  # ----> Width
            if fender_ref[i, j, 0] > 20:
                lst_x.append(j)
                lst_y.append(i)
    min_x = min(lst_x)
    max_x = max(lst_x)
    min_y = min(lst_y)
    max_y = max(lst_y)

    # fender_ref = cv2.circle(fender_ref, (min_y, min_x), radius=5, color=(255, 0, 255), thickness=3)
    # fender_ref = cv2.circle(fender_ref, (max_y, max_x), radius=5, color=(156, 0, 167), thickness=3)
    return fender_ref, min_x,min_y, max_x,max_y


def read_frame_from_video(path):
    if os.path.exists(path):
        cap = cv2.VideoCapture(path)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imwrite("temp_frame.jpg", frame)
                res = ship_det.detect("temp_frame.jpg".encode('ascii'))
                for i in range(len(res)):
                    print(type(res[i]), len(res[i]), res[i])
                    cls, confi, coordi = res[i]
            else:               # breaks if video file Ends
                break
    else:
        print('\n\n Video File does not Exsist')


def read_frames_from_dir(path):
    for f in os.listdir(path):  # dir_of_file + '/ship/test_data/'
        if f.endswith('.jpg'):
            temp = os.path.join(path, f)
            if os.path.exists(temp):
                res = ship_det.detect(temp.encode('ascii'))
                print(res, type(res))
                for e in range(len(res)):
                    print('**************')


def check_for_overlap(rec1_x1, rec1_y1, rec1_x2, rec1_y2, rec2_x1, rec2_y1, rec2_x2, rec2_y2):
    rectangle_a = {"x1":rec1_x1, "y1":rec1_y1, "x2":rec1_x2,"y2":rec1_y2}   # ----> det
    rectangle_b = {"x1": rec2_x1, "y1":rec2_y1, "x2":rec2_x2,"y2":rec2_y2}  # ----> fender

    # from Left
    if rectangle_a["y1"] < rectangle_b["y2"] and rectangle_a["x2"] > rectangle_b["x1"]:
        print("OVERLAP from LEFT ! ")
        return True
    else:
        print("there is no overlap")
        return False


fender_image, minx, miny, maxx, maxy = fender_coordi(fender_path)
print( minx, miny, maxx, maxy)
fender_ref = cv2.circle(fender_image, (minx, miny), radius=5, color=(255, 6, 255), thickness=3)
#cv2.imshow('bdhvb', fender_ref)

if not USING_VIDEO_FILE:
    read_frames_from_dir(dir_of_file + '/ship/test_data/')

else:
    # path = dir_of_file + '/ship/test_data/video.mp4'
    path = IP_STREAM_1
    #if os.path.exists(path):
    cap = cv2.VideoCapture(path)
    while cap.isOpened():
        #print(cap)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("temp_frame.jpg", frame)
            res = ship_det.detect("temp_frame.jpg".encode('ascii'))
            for i in range(len(res)):
                cls, confi, coordi = res[i]
                if cls == b'boat':
                    xmi,ymi,xma,yma = bbox2points(coordi)
                    #print((xmi,ymi),(xma,yma),(minx, miny), (maxx, maxy))
                    overlap = check_for_overlap(xmi,ymi,xma,yma,minx, miny, maxx, maxy)
                    #image = cv2.imread("temp_frame.jpg")
                    #image = cv2.rectangle(image, (math.floor(xmi), math.floor(ymi)), (math.floor(xma), math.floor(yma)), (255, 255, 0), 2)
                    #image = cv2.rectangle(image,(minx,miny),(maxx,maxy),(0,0,0),2)
                    #cv2.imshow('winname', image)
                    #cv2.waitKey(0)
                    #cv2.destroyAllWindows()
                    if overlap:
                        r = requests.post(url= POST_LINK, data = {'Threat': 'yes', 'object': cls})
                else:
                    print('Nothing detected')
        else:               # breaks if video file Ends
            break

    #else:
     #   print('\n\n Video File does not Exsist')