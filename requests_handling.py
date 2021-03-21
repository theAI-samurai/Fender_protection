"""
--------------------------------------------------
filename        : request_handling.py
Name            : Ankit Mishra
Email           : ankitmishra723@gmail.com
Date created    : Feb 28, 2021
Date Modified   : Mar 21, 2021
---------------------------------------------------
"""

from read_config import *
from PIL import Image
import numpy as np
import requests
import os


def save_image(pil_image, name_for_file, camera_id):
    """ ----------------------------------------------
        this function saves the PNG format PIL image obtained from GET link
        for each cam_ID.

        ARGUMENT    :
                camera_id : cam for which Image obtained
                name_for_file : file name (markup/snapshot)
                pil_image: Image in PIL_PNG format

        RETURN      : None
        ------------------------------------------- """
    ref_dir = dir_of_file + '/ship/reference_files/'
    if not os.path.isdir(ref_dir):
        oldmask = os.umask(000)
        os.makedirs(ref_dir, 0o0777)
        os.umask(oldmask)
    pil_image.save(ref_dir+name_for_file+'_'+str(camera_id)+'.jpg')


def get_markup_image(cameraID):
    """ --------------
    this function fetches the markup image for the camera ID provided.
    ARGUMENT    : camera id
    RETURN      : markup_image
    --------------- """
    markup_cam_1 = markup_base_url+str(cameraID)
    r = requests.get(markup_cam_1, stream=True).raw
    if r.status == 200:
        img = Image.open(r).convert('RGB')
        # img.save('fender.jpg')
        save_image(img, name_for_file='markup',camera_id=cameraID)
        return True
    else:
        return False


def get_reference_snapshot_image(cameraID):
    """ --------------
    this function fetches the Snapshot image for the camera ID provided.

    ARGUMENT    : camera id
    RETURN      : markup_image
    --------------- """
    ref_cam_1 = ref_base_url+str(cameraID)
    r = requests.get(ref_cam_1, stream=True).raw
    if r.status == 200:
        img = Image.open(r).convert('RGB')
        # img.save('fender.jpg')
        save_image(img, name_for_file='fender', camera_id=cameraID)
        return True
    else:
        return False


def notification_trigger(cameraID, object, status, object_known, image_path):
    """ -----------------------------------------------------------
    this function sends a POST notification to front_end
    ARGUMENTS :
                cameraID    : id of camera for which notification generated --> 1,2,3,4
                object      : 'ship'/ 'fender'/ 'others'
                status      : threat/ no-threat
                object_known: known/ unknown
                image_path  : path to jpg file
    RETURN : NONE
    ----------------------------------------------------------- """

    headers = {'x-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MDQyMzA3ZDZhM2IyMjI2YjgyZmE0MmMiLCJyb2xlIjoiQURNSU4iLCJpYXQiOjE2MTUyODMyMTR9.FPv1C_AELB9UStxx-Jwj5Vax7OgRJr6Rr3sFPRxMa4M'}
    payload = {'title': object, 'status': status,
               'type': object_known, 'siteNumber': cameraID}
    files = {'imageUrl': open(image_path, 'rb')}
    session = requests.Session()
    session.post(notification_url, headers=headers, data=payload,files=files)


def camera_active_status(all_list, data):
    """ ----------------------------------------------
        this function passes data for camera status as active or not
        to frontend.

        ARGUMENT    :
                    all_list : list of All camera IDs
                    data     : list of active cameras IDs
        RETURN      : None
        ------------------------------------------- """
    false_cameras = np.setdiff1d(all_list, data)
    for cam_id in data:
        cam_post = camera_status_url + str(cam_id)
        print(cam_post)
        requests.post(cam_post, data={'active': 1})
    for cam_id in false_cameras:
        cam_post = camera_status_url + str(cam_id)
        print(cam_post)
        requests.post(cam_post, data={'active': 0})


def camera_status_notification(cam_id, status_code):
    """ ---------------------------------------------------
    this function POSTs notification to frontend for camera status
    cam_id      : ID of camera
    status_code :   0 if camera is Inactive;
                    1 if camera is Active
    --------------------------------------------------- """
    cam_post = camera_status_url + str(cam_id)
    requests.post(cam_post, data={'active': status_code})

