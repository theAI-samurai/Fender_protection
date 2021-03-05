from read_config import *
import cv2


def active_streams_initialize(data):
    # lst = [camera_path_1, camera_path_2]
    lst = dict.keys(data)
    active_lst = []
    for cp in lst:
        ctr = 0
        cap = cv2.VideoCapture(data[cp])
        while cap.isOpened():
            ret_, _ = cap.read()
            if ret_ and ctr < 3:
                ctr += 1
                active_lst.append(cp)
            else:
                break

    return list(set(active_lst))




# active_camera_ids = active_streams_initialize(all_camera_data)
