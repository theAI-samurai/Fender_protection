"""
--------------------------------------------------
filename        : data_validate.py
Name            : Ankit Mishra
Email           : ankitmishra723@gmail.com
Date created    : Feb 28, 2021
Date Modified   : Mar 05, 2021
---------------------------------------------------
"""

from read_config import *
import cv2


def active_streams_initialize(data):
    """ --------------
    this function checks which IP streams provided in the conf.txt are active.
    ARGUMENT    : Dict containing {cam_id:cam_url}
    RETURN      : List containing cam_ids that are active
    --------------- """
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




