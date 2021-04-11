
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





















