from read_config import *
from data_validate import *
from darknet import *
from image_codes import *
import time
import math
import shutil
import gc


active_cams = []
VLC_PLAYER_OBJECT = {}

# loading Deep learning model
net = model_load(cfgPath=dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                 wgtPath=dir_of_file + '/ship/cfg/yolov3_full_ship.weights')


if os.path.exists(dir_of_file + '/ship/unknown_objects'):
    pass
else:
    os.mkdir(dir_of_file + '/ship/unknown_objects', mode=0o777)


def main_program(cam_, cam_url):

    restart_status = False
    lst_markup_coord = None

    start_timer = 0
    notification_timer = 0
    fgbg1 = cv2.bgsegm.createBackgroundSubtractorMOG()
    obj_detect = ObjectDetection(dataPath=dir_of_file + '/ship/cfg/ship.data', netwrk=net, camID=cam_)

    while True:

        global active_cams
        global VLC_PLAYER_OBJECT
        global result

        print(active_cams)

        if cam_ not in active_cams:                                     # if camID is inactive initialize the camera
            is_active = active_stream_initialize_vlc(cam_, cam_url)     # checks if frame available
            if is_active:                                               # if True
                restart_status = False
                start_timer = 0
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

            # Getting Markup Coordinate for OVERLAP CALCULATIONS
            if lst_markup_coord is None:
                lst_markup_coord = markup_coordinate(markup_img_path=markup_img_pa)

            if not restart_status:
                # Read FRAME IMAGE Path
                frame_path = dir_of_file + '/ship/reference_files/' + str(cam_) + '.jpg'
                read = read_frames_using_vlc(player=VLC_PLAYER_OBJECT[cam_], delay_time=2,
                                             path=frame_path, camid=cam_)

                fgmask = None
                contours = []
                draw = 0

                if read:                                                # Frame Received
                    start_timer = 0                                     # RESET timer = 0 as frame was received

                    # Read FRAME Image --> This is Original unchanged Image
                    image = cv2.resize(cv2.imread(frame_path), (int(WIDTH), int(HEIGHT)))

                    # Foreground Mask of Image
                    fgmask = fgbg1.apply(image)

                    # checking if there is a pixel worth noting after subtraction
                    if fgmask is not None:
                        number_of_white_pix = np.sum(fgmask >= 250)
                        white_pixel_percent = (number_of_white_pix / 518400)*100
                    else:
                        break

                    # YOLO v3 Detection Module is called on the FRAME read
                    res = obj_detect.detect(frame_path.encode('ascii'))

                    print('-----------------------', result)

                    cls = 'None'
                    # IF Any detection was made by YOLO Network
                    if len(res) != 0:

                        any_overlapping = 0
                        image_ = None

                        for i in range(len(res)):
                            cls, confi, coordi = res[i]

                            log_file = open(dir_of_file + '/LogFile.txt', 'a')
                            log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+': DL Model dectected, '+ str(cls)+'\n')
                            log_file.close()

                            # while cls identified is other than safe
                            if cls.decode() != 'safe':
                                xmi, ymi, xma, yma = bbox2points(coordi)

                                # OVERLAP CALCULATION on DETECTED RESULTS
                                overlap = overlap_red_markup_v2(coordi_dict=lst_markup_coord,
                                                                min_x=xmi, min_y=ymi,
                                                                max_x=xma, max_y=yma)
                                if overlap:
                                    any_overlapping += 1

                                # Rectangle marking for BOAT/ SHIP/ THREAT coordinates
                                image_ = cv2.rectangle(image, (math.floor(xmi), math.floor(ymi)),
                                                       (math.floor(xma), math.floor(yma)),
                                                       (255, 255, 0), 2)
                                # Detection Text on FRAME Image
                                image_ = cv2.putText(image_, cls.decode(), (math.floor(xmi), math.floor(ymi)-3),
                                                     cv2.FONT_HERSHEY_SIMPLEX,
                                                     0.5, (0, 255, 255), 1)
                                # OVERLAPPING Markup on FRAME image
                                image_ = cv2.addWeighted(image_, 1, markup_image, 1, 0)

                                # MASKING the Detected coordinate  --> This is BW image
                                # Thickness = -1 Fills the rectangle with specified Color
                                fgmask = cv2.rectangle(fgmask, (xmi, ymi), (xma, yma),
                                                       (0, 0, 0), thickness=-1)

                        # NOTIFICATION TRIGGER for OVERLAPPING Scenario
                        if any_overlapping > 0:
                            save_detect_path = dir_of_file + '/ship/reference_files/detect_' + str(cam_) + '.jpg'
                            cv2.imwrite(save_detect_path, image_)
                            notification_trigger(cameraID=cam_, object='Vessel', status='Threat',
                                                 object_known=cls.decode(), image_path=save_detect_path)

                            notification_timer = 0

                            log_file = open(dir_of_file + '/LogFile.txt', 'a')
                            log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()) + ': Notification sent for Vessel Breach, ' + str(cls)+'\n')
                            log_file.close()

                        # NOTIFICATION for DETECTION but, NO OVERLAPPING Scenario
                        else:
                            # Finding CONTOUR on BW Masked Image
                            contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                            draw = 0
                            # Area of Contour
                            for contour in contours:
                                area = cv2.contourArea(contour)
                                if 400 < area < 5000:
                                    cv2.drawContours(image_, contour, -1, (200, 4, 14), 1)
                                    draw += 1
                            if image_ is not None or (draw > 0 and white_pixel_percent > 0.2):
                                curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                                save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_' + str(cam_) + '_' + curr_time + '.jpg'
                                cv2.imwrite(save_unknown_path, image_)

                                # NOTIFICATION TRIGGER for Unknown Detection +
                                # Threat Detections + No Overlap
                                notification_trigger(cameraID=cam_,
                                                     object='Vessel_No_breach',
                                                     status=cls.decode(),
                                                     object_known='Known',
                                                     image_path=save_unknown_path)

                                notification_timer = 0

                                log_file = open(dir_of_file + '/LogFile.txt', 'a')
                                log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()) + ': Notification sent for Vessel Not Breach, ' + str(cls)+'\n')
                                log_file.close()

                    # IF No Detection was made by YOLO Network
                    else:
                        # OVERLAPPING Markup on FRAME image
                        image_ = cv2.addWeighted(image, 1, markup_image, 1, 0)

                        # Finding CONTOUR on BW Masked Image
                        contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        draw = 0

                        # Area of Contour
                        for contour in contours:
                            area = cv2.contourArea(contour)
                            if 400 < area < 5000:
                                cv2.drawContours(image_, contours, -1, (191, 11, 11), 1)
                                draw += 1
                        if draw > 0 and white_pixel_percent > 0.2:
                            curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                            save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_' + str(cam_) + '_' + curr_time + '.jpg'
                            cv2.imwrite(save_unknown_path, image_)

                            # NOTIFICATION TRIGGER for Unknown Detection + No Detections
                            # Note We will send notifications for unidenfied after every 15 seconds only
                            if notification_timer == 0 or time.time() - notification_timer == 15:
                                notification_timer = time.time()
                                notification_trigger(cameraID=cam_, object='Unidentified Object',
                                                     status='System not Trained',
                                                     object_known='UnKnown',
                                                     image_path=save_unknown_path)

                                log_file = open(dir_of_file + '/LogFile.txt', 'a')
                                log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()) + ': Notification sent for UnIdendified Object, ' + str(cls)+'\n')
                                log_file.close()

                # if Frame is not Read
                else:
                    if start_timer == 0:
                        # start timer if Frame not Recieved
                        start_timer = time.time()
                    # check if timer is active for 120 sec or 2 mins
                    if start_timer != 0 and time.time() - start_timer > 20:
                        active_cams.remove(cam_)            # delete cameraID from Active cam list
                        VLC_PLAYER_OBJECT[cam_].stop()
                        VLC_PLAYER_OBJECT[cam_].release()
                        del VLC_PLAYER_OBJECT[cam_]         # del VLC object of cameraID
                        gc.collect()
                        restart_status = True               # Status : True to reacquire objects for camID
                        camera_status_notification(cam_id=cam_, status_code=0, remark='Failed Request sent')      # notification trigger to add

                        log_file = open(dir_of_file + '/LogFile.txt', 'a')
                        log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ': Failed Request sent and Objects destroyed and killed for , ' + str(cam_) + '\n')
                        log_file.close()
