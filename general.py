
import cv2
import os
from os.path import dirname, realpath
dir_of_file = dirname(realpath(__file__))
os.chdir(dir_of_file)

imges = []
path_ =dir_of_file + '/ship/test_data/'
path_ ='D:/1/ships/'

for f in os.listdir(path_) :
    if f.endswith('.jpg'):
        temp = os.path.join(path_, f)
        if os.path.exists(temp):
            img = cv2.imread(temp)
            imges.append(img)
            #res = ship_det.detect(temp.encode('ascii'))
            #print(res, type(res))
            #for e in range(len(res)):
            #    print('**************')
        #else:
        #    print("Image path does not exsist")

video=cv2.VideoWriter(os.path.join(path_, 'video.mp4'),-1,1,(imges[1].shape[1], imges[1].shape[0]))

for j in range(len(imges)):
    video.write(imges[j])

cv2.destroyAllWindows()
video.release()

import cv2
path  = r'D:\my_repos\darknet_fender_protection\ship\test_data\wassup.mp4'
cap = cv2.VideoCapture(path)
ctr = 0
while cap.isOpened():
    ret, frame = cap.read()
    print(ret)
    if ret:
        cv2.imwrite("temp_frame"+str(ctr)+".jpg", frame)
        ctr = ctr+1
    else:
        break

# overlay of markup image on frame captured TEST
import cv2
main_img = cv2.resize(cv2.imread(r'D:\darknet_fender_protection\ship\reference_files\5.jpg'),(960,540))
markup_image = cv2.resize(cv2.imread(r'D:\darknet_fender_protection\ship\reference_files\markup_5.jpg'),(960,540))
print(main_img.shape, markup_image.shape)
main_img = cv2.addWeighted(main_img, 1, markup_image, 1, 0)
save_detect_path = r'D:\darknet_fender_protection/ship/reference_files/detect_5'+'.jpg'
cv2.imwrite(save_detect_path, main_img)

cv2.waitKey(0)
cv2.destroyAllWindows()



# height width validate

from data_validate import *
import cv2

main_img = r'D:\darknet_fender_protection\ship\reference_files\5.jpg'
markup_image = r'D:\darknet_fender_protection\ship\reference_files\markup_5.jpg'

height_width_validate(main_img, markup_image)

# ----------baground subtraction
import cv2

backSub_1 = cv2.createBackgroundSubtractorMOG2()
backSub_2 = cv2.createBackgroundSubtractorKNN()


ref_frame_path = r'D:\darknet_fender_protection\ship\reference_files\fender_8.jpg'
new_frame = r'D:\darknet_fender_protection\ship\reference_files\5.jpg'



# ------------------------------------- RED MARKUP TEST -----------------

import cv2

markup = r'D:\darknet_fender_protection\ship\reference_files\markup_9.jpg'
boat = r'D:\darknet_fender_protection\ship\reference_files\detect_9.jpg'

bat = cv2.imread(boat)
mrk = cv2.imread(markup)

c1 = (184, 332)  # --> 184:W, 332:H in a image where W = 960, H = 540------- to access img[H,W]
c2 = (447, 497)     # (W,H)
c3 = (447,332)
c4 = (184,497)

bat = cv2.circle(bat, c1, radius=1, color=(0, 0, 255), thickness=4)  # (w,h)
bat = cv2.circle(bat, c2, radius=1, color=(0, 0, 255), thickness=4)
bat = cv2.circle(bat, c3, radius=1, color=(0, 0, 255), thickness=4)
bat = cv2.circle(bat, c4, radius=1, color=(0, 0, 255), thickness=4)


def list_marking_coord(mark_img):
    lst = []
    for i in range(mark_img.shape[0]):       # H
        for j in range(mark_img.shape[1]):   # W
            if mark_img[i, j, 2] > 150:
                lst.append((j,i))       # (W,H)
    return lst


lst = list_marking_coord(mrk)


def overlap_from_left_red_markup(cord_lst, top_right):
    for iter, tup in enumerate(cord_lst):
        w = tup[0]
        h = tup[1]
        W = top_right[0]
        H = top_right[1]
        if w in range(W-130, W+20) and h in range(H-15, H+15):
            print('OVERLAP FROM LEFT')
            break
        return True


#
import requests
from read_config import *
from PIL import Image
import cv2

markup_cam_1 = markup_base_url+str(5)
for i in range(6):
    try:
        r = requests.get(markup_cam_1, stream=True).raw
    except:
        r=0
    print(r.status)
    i+=1
    if r.status ==200:
        img = Image.open(r).convert('RGB')
        img.save('D:/darknet_fender_protection/ship/reference_files/test'+str(i)+'.jpg')













