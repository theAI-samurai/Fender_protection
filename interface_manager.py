from read_config import *
from data_validate import *
from darknet import *
from image_codes import *
import time
import math


active_cams = []
VLC_PLAYER_OBJECT = {}
start_timer = 0

# loading Deep learning model
net = model_load(cfgPath=dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                 wgtPath=dir_of_file + '/ship/cfg/yolov3_full_ship_2000.weights')

obj_detect = ObjectDetection(dataPath=dir_of_file + '/ship/cfg/ship.data', netwrk=net, camID=0)


def main_program(cam_, cam_url):
    restart_status = False
    while True:

        global active_cams
        global VLC_PLAYER_OBJECT
        global start_timer

        if cam_ not in active_cams:                                     # if camID is inactive initialize the camera
            is_active = active_stream_initialize_vlc(cam_, cam_url)     # checks if frame available
            if is_active:                                               # if True
                active_cams.append(cam_)
                vlc_obj = vlc_stream_object_init_3(cam_url)
                VLC_PLAYER_OBJECT.update({cam_: vlc_obj})
                del vlc_obj
        else:                                                           # if camID is active
            fender_markup_image, minx, miny, maxx, maxy = fender_coordi(path_=dir_of_file + '/ship/reference_files/markup_' + (cam_) + '.jpg')

            while not restart_status:
                read = read_frames_using_vlc(player=VLC_PLAYER_OBJECT[cam_], delay_time=1,
                                             cam_id=cam_, base_path=dir_of_file + '/ship/reference_files/')
                if read:
                    start_timer = 0                                     # RESET timer = 0 as frame was received
                    frame_path = dir_of_file + '/ship/reference_files/' + str(cam_) + '.jpg'  # frame path
                    markup_img_pa = dir_of_file + '/ship/reference_files/markup_' + str(cam_) + '.jpg'  # markup_path
                    new_dim = height_width_validate(frame_path, markup_img_pa)
                    markup_img = cv2.resize(cv2.imread(markup_img_pa), new_dim)  # Read markup image
                    lst_markup_coord = list_marking_coord(markup_img)  # List of Markup Coord
                    res = obj_detect.detect(frame_path.encode('ascii'))  # calling detection on the saved snapshot
                    for i in range(len(res)):
                        cls, confi, coordi = res[i]
                        if cls == b'boat':
                            xmi, ymi, xma, yma = bbox2points(coordi)  # coordinate of object in image
                            # overlap = check_for_overlap(xmi, ymi, xma, yma, minx, miny, maxx, maxy)
                            overlap = overlap_from_left_red_markup(cord_lst=lst_markup_coord, top_right=(xma, ymi))
                            if overlap:
                                image = cv2.resize(cv2.imread(frame_path), new_dim)  # snapshot image file read
                                image = cv2.rectangle(image, (math.floor(xmi), math.floor(ymi)),
                                                      (math.floor(xma), math.floor(yma)), (255, 255, 0), 2)
                                image = cv2.rectangle(image, (minx, miny), (maxx, maxy), (0, 0, 0), 2)
                                image_ = cv2.addWeighted(image, 1, markup_img, 1, 0)
                                save_detect_path = dir_of_file + '/ship/reference_files/detect_' + str(cam_) + '.jpg'
                                cv2.imwrite(save_detect_path, image_)
                                time.sleep(2)
                                notification_trigger(cameraID=cam_, object=cls, status='Threat',
                                                     object_known='Known', image_path=save_detect_path)
                else:
                    start_timer = time.time()                   # start timer if Frame not Recieved
                    if start_timer != 0:
                        if time.time() - start_timer > 1200:    # check if timer is active for 1200 sec or 20 mins
                            active_cams.remove(cam_)            # delete cameraID from Active cam list
                            del VLC_PLAYER_OBJECT[cam_]         # del VLC object of cameraID
                            restart_status = True               # Status : True to reacquire objects for camID





