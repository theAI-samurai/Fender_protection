from read_config import *
from data_validate import *
from darknet import *
from image_codes import *
import time
import math
import shutil


active_cams = []
VLC_PLAYER_OBJECT = {}
start_timer = 0
reference_image_start_timer = time.time()
ctr = 0

fgbg1 = cv2.bgsegm.createBackgroundSubtractorMOG()

# loading Deep learning model
net = model_load(cfgPath=dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                 wgtPath=dir_of_file + '/ship/cfg/yolov3_full_ship.weights')

obj_detect = ObjectDetection(dataPath=dir_of_file + '/ship/cfg/ship.data', netwrk=net, camID=0)

if os.path.exists(dir_of_file + '/ship/unknown_objects'):
    pass
else:
    os.mkdir(dir_of_file + '/ship/unknown_objects', mode=0o777)


def main_program(cam_, cam_url):

    restart_status = False

    while True:
        global active_cams
        global VLC_PLAYER_OBJECT
        global start_timer
        global fgbg1
        global ctr
        global reference_image_start_timer

        if cam_ not in active_cams:                                     # if camID is inactive initialize the camera
            is_active = active_stream_initialize_vlc(cam_, cam_url)     # checks if frame available
            if is_active:                                               # if True
                active_cams.append(cam_)
                vlc_obj = vlc_stream_object_init_3(cam_url)
                VLC_PLAYER_OBJECT.update({cam_: vlc_obj})
                del vlc_obj
        else:                                                           # if camID is active
            # MARKUP IMAGE path
            markup_img_pa = dir_of_file + '/ship/reference_files/markup_' + str(cam_) + '.jpg'
            # MAXIMUM & MINIMUM coordinates for Markup Image
            # fender_markup_image is now --> Markup image
            markup_image, minx, miny, maxx, maxy = fender_coordi(path_=markup_img_pa)

            if not restart_status:
                # Read FRAME IMAGE Path
                frame_path = dir_of_file + '/ship/reference_files/' + str(cam_) + '.jpg'
                read = read_frames_using_vlc(player=VLC_PLAYER_OBJECT[cam_], delay_time=5,
                                             path=frame_path)
                if read:                                                # Frame Received
                    # Read FRAME Image --> This is Original unchanged Image
                    image = cv2.imread(frame_path)
                    start_timer = 0                                     # RESET timer = 0 as frame was received
                    # Replacing the Reference Fender Image after a fixed time
                    if time.time() - reference_image_start_timer > 60:
                        shutil.copy2(frame_path, dir_of_file + '/ship/reference_files/fender_' + str(cam_) + '.jpg')
                        reference_image_start_timer = time.time()
                    # List of Markup Coordinates ie RED line coordinates in markup image
                    lst_markup_coord = list_marking_coord(markup_image)
                    # YOLO v3 Detection Module is called on the FRAME read
                    res = obj_detect.detect(frame_path.encode('ascii'))

                    # IF Any Detection was Made on the read Frame
                    if len(res) != 0:
                        for i in range(len(res)):
                            cls, confi, coordi = res[i]

                            # IF detection is a THREAT CATEGORY
                            if cls == b'boat' or cls == b'Threat' or cls == b'ship':
                                # coordinate of object in image
                                xmi, ymi, xma, yma = bbox2points(coordi)
                                # overlap using rectangular box (The code is redundant now)
                                # overlap = check_for_overlap(xmi, ymi, xma, yma, minx, miny, maxx, maxy)
                                overlap = overlap_from_left_red_markup(cord_lst=lst_markup_coord, top_right=(xma, ymi))

                                # IF THREAT is Overlapping
                                if overlap:
                                    # Mask Applied
                                    fgmask = fgbg1.apply(image)
                                    # MASKING the Detected coordinate  --> This is BW image
                                    # Thickness = -1 Fills the rectangle with specified Color
                                    cv2.rectangle(fgmask, (math.floor(xmi), math.floor(ymi)),
                                                  (math.floor(xma), math.floor(yma)),
                                                  (0, 0, 0), thickness=-1)
                                    # Rectangle marking for BOAT/ SHIP/ THREAT coordinates
                                    image = cv2.rectangle(image, (math.floor(xmi), math.floor(ymi)),
                                                          (math.floor(xma), math.floor(yma)),
                                                          (255, 255, 0), 2)
                                    # Rectangle of Markup Image
                                    image = cv2.rectangle(image, (minx, miny),
                                                          (maxx, maxy),
                                                          (0, 0, 0), 2)
                                    # OVERLAPPING Markup on FRAME image
                                    image_ = cv2.addWeighted(image, 1, markup_image, 1, 0)

                                    # Finding CONTOUR on BW Masked Image
                                    contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                                    draw = 0
                                    # Area of Contour
                                    for contour in contours:
                                        area = cv2.contourArea(contour)
                                        if 1000 < area < 5000:
                                            cv2.drawContours(image_, contour, -1, (200, 4, 14), 2)
                                            draw += 1
                                    if draw > 0:
                                        curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                                        save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_overlap_' + str(cam_) + '_' + curr_time + str(ctr) + '.jpg'
                                        ctr += 1
                                        cv2.imwrite(save_unknown_path, image_)

                                        # NOTIFICATION TRIGGER for Unknown detection + THREAT Detection + Overlap
                                        notification_trigger(cameraID=cam_, object='unknown_countours', status='Unknown'
                                                             , object_known='UnKnown', image_path=save_unknown_path)

                                    # NOTIFICATION TRIGGER for OVERLAPPING Detections
                                    save_detect_path = dir_of_file + '/ship/reference_files/detect_' + str(cam_) + '.jpg'
                                    cv2.imwrite(save_detect_path, image_)
                                    notification_trigger(cameraID=cam_, object=cls, status='Threat',
                                                         object_known='Known', image_path=save_detect_path)

                                # IF THREAT is NOT Overlapping
                                else:
                                    # Mask Applied
                                    fgmask = fgbg1.apply(image)
                                    # MASKING the Detected coordinate  --> This is BW image
                                    # Thickness = -1 Fills the rectangle with specified Color
                                    cv2.rectangle(fgmask, (math.floor(xmi), math.floor(ymi)),
                                                  (math.floor(xma), math.floor(yma)),
                                                  (0, 0, 0), thickness=-1)

                                    # OVERLAPPING Markup on FRAME image
                                    image_ = cv2.addWeighted(image, 1, markup_image, 1, 0)

                                    # Finding CONTOUR on BW Masked Image
                                    contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                                    draw = 0
                                    # Area of Contour
                                    for contour in contours:
                                        area = cv2.contourArea(contour)
                                        if 1000 < area < 5000:
                                            cv2.drawContours(image_, contour, -1, (200, 4, 14), 2)
                                            draw += 1
                                    if draw > 0:
                                        curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                                        save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_' + str(cam_) + '_' + curr_time + str(ctr) + '.jpg'
                                        ctr += 1
                                        cv2.imwrite(save_unknown_path, image_)

                                        # NOTIFICATION TRIGGER for Unknown Detection +
                                        # Threat Detections + No Overlap
                                        notification_trigger(cameraID=cam_, object='unknown_countours',
                                                             status='Unknown',
                                                             object_known='UnKnown',
                                                             image_path=save_unknown_path)
                            else:
                                pass
                    # ELSE, if No Detection was made on Read Frame
                    else:
                        # Mask Applied
                        fgmask = fgbg1.apply(image)

                        # OVERLAPPING Markup on FRAME image
                        image_ = cv2.addWeighted(image, 1, markup_image, 1, 0)

                        # Finding CONTOUR on BW Masked Image
                        contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        draw = 0

                        # Area of Contour
                        for contour in contours:
                            area = cv2.contourArea(contour)
                            if 1000 < area < 5000:
                                cv2.drawContours(image_, contours, -1, (200, 4, 14), 2)
                                draw += 1
                        if draw > 0:
                            curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                            save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_' + str(cam_) + '_' + curr_time + str(ctr) + '.jpg'
                            ctr += 1
                            cv2.imwrite(save_unknown_path, image_)

                            # NOTIFICATION TRIGGER for Unknown Detection + No Detections
                            notification_trigger(cameraID=cam_, object='unknown_countours', status='Unknown'
                                                 , object_known='UnKnown', image_path=save_unknown_path)
                # if Frame is not Read
                else:
                    if start_timer == 0:
                        # start timer if Frame not Recieved
                        start_timer = time.time()
                    # check if timer is active for 120 sec or 2 mins
                    if start_timer != 0 and time.time() - start_timer > 120:
                        active_cams.remove(cam_)            # delete cameraID from Active cam list
                        del VLC_PLAYER_OBJECT[cam_]         # del VLC object of cameraID
                        restart_status = True               # Status : True to reacquire objects for camID
                        camera_status_notification(cam_id=cam_, status_code=0)      # notification trigger to add
                        print('failed request sent', cam_)
