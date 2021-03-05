
import cv2
import os
from os.path import dirname, realpath
dir_of_file = dirname(realpath(__file__))
os.chdir(dir_of_file)

imges = []

for f in os.listdir(dir_of_file + '/ship/test_data/') :
    if f.endswith('.jpg'):
        temp = os.path.join(dir_of_file + '/ship/test_data/', f)
        if os.path.exists(temp):
            img = cv2.imread(temp)
            imges.append(img)
            #res = ship_det.detect(temp.encode('ascii'))
            #print(res, type(res))
            #for e in range(len(res)):
            #    print('**************')
        #else:
        #    print("Image path does not exsist")

video=cv2.VideoWriter(os.path.join(dir_of_file + '/ship/test_data/', 'video.mp4'),-1,1,(imges[1].shape[1], imges[1].shape[0]))

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