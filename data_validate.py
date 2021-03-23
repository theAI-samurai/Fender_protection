"""
--------------------------------------------------
filename        : data_validate.py
Name            : Ankit Mishra
Email           : ankitmishra723@gmail.com
Date created    : Feb 28, 2021
Date Modified   : Mar 21, 2021
---------------------------------------------------
"""

import cv2
import vlc
import time
from requests_handling import *


def active_streams_initialize_vlc(data):
    """ -------------------------------------------------------------------------
    this function validate the IP streams that are Active / Inactive
    Args:
        data    : Dictionary containg {ID   : url} for all cameras fron config.txt
    Return      : List of camera IDs that are Active and Inactive
    -------------------------------------------------------------------------- """
    lst = dict.keys(data)
    active_lst = []
    inactive_lst = []
    for cp in lst:
        player = vlc.MediaPlayer(data[cp])
        # print(cp, player)
        player.play()
        time.sleep(2)
        if player.is_playing():
            player.stop()
            player.release()
            active_lst.append(cp)
            camera_status_notification(cam_id=cp, status_code=1)    # sending notification to frontend for active Cam
            get_markup_image(cp)                                    # Markup Image for Camera ID = cp
            get_reference_snapshot_image(cp)                        # Reference Image for Cam ID = cp
        else:
            inactive_lst.append(cp)
            camera_status_notification(cam_id=cp, status_code=0)  # sending notification to frontend for inactive Cam
    return list(set(active_lst)), list(set(inactive_lst))


def active_streams_initialize(data):
    """ --------------
    this function checks which IP streams provided in the conf.txt are active.
    ARGUMENT    : Dict containing {cam_id:cam_url}
    RETURN      : List containing cam_ids that are active
    --------------- """
    # lst = [camera_path_1, camera_path_2]
    lst = dict.keys(data)
    active_lst = []
    inactive_lst = []
    for cp in lst:
        ctr = 0
        cap = cv2.VideoCapture(data[cp])
        while cap.isOpened():
            ret_, _ = cap.read()
            if ret_ and ctr < 3:
                ctr += 1
                active_lst.append(cp)
                camera_status_notification(cam_id=cp, status_code=1)  # sending notification to frontend for active Cam
                get_markup_image(cp)  # Markup Image for Camera ID = cp
                get_reference_snapshot_image(cp)  # Reference Image for Cam ID = cp
            else:
                inactive_lst.append(cp)
                camera_status_notification(cam_id=cp, status_code=1)  # sending notification to frontend for active Cam

    return list(set(active_lst)), list(set(inactive_lst))


def height_width_validate():
    print('pass')



