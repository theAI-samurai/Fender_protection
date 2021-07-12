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

log_file = open(dir_of_file + '/LogFile.txt', 'a')

def main_program(cam_, cam_url):

    restart_status = False
    lst_markup_coord = None

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

            # Getting Markup Coordinate for OVERLAP CALCULATIONS
            if lst_markup_coord is None:
                lst_markup_coord = markup_coordinate(markup_img_path=markup_img_pa)

            if not restart_status:
                ctr_ = 0
                # Read FRAME IMAGE Path
                frame_path = dir_of_file + '/ship/reference_files/' + str(cam_) + '.jpg'
                read = read_frames_using_vlc(player=VLC_PLAYER_OBJECT[cam_], delay_time=5,
                                             path=frame_path)
                if read:                                                # Frame Received
                    start_timer = 0                                     # RESET timer = 0 as frame was received
                    # Replacing the Reference Fender Image after a fixed time
                    # &
                    # Dictionary of Markup Coordinates for Cam ID : cam_ in Every 6 HOURS
                    if time.time() - reference_image_start_timer > 21600:
                        lst_markup_coord = markup_coordinate(markup_img_path=markup_img_pa)
                        # commenting the Reference File Replace 24-05-2021
                        # shutil.copy2(frame_path, dir_of_file + '/ship/reference_files/fender_' + str(cam_) + '.jpg')
                        reference_image_start_timer = time.time()

                    # ------------------ MAIN EXECUTIONS on IMAGE ----------------------
                    # Read FRAME Image --> This is Original unchanged Image
                    image = cv2.imread(frame_path)

                    # Foreground Mask of Image
                    fgmask = fgbg1.apply(image)
                    #cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/'+str(ctr)+'_fg.jpg', fgmask)

                    # checking if there is a pixel worth noting after subtraction
                    if fgmask is not None:
                        number_of_white_pix = np.sum(fgmask >= 250)
                    else:
                        break
                    #print('white_pixels : ', (number_of_white_pix / 518400)*100)
                    """
                    We are commenting the if condition on white_pixel senario bcoz in a test scenario
                    where a ship was closing in very very slowly the system failed to trigger an alert as the 
                    if condition failed
                    # if (number_of_white_pix / 518400)*100 > 0.2:
                    """

                    # YOLO v3 Detection Module is called on the FRAME read
                    res = obj_detect.detect(frame_path.encode('ascii'))
                    # IF Any detection was made by YOLO Network
                    if len(res) != 0:
                        print(res)
                        result = []
                        any_overlapping = 0
                        image_ = None
                        for i in range(len(res)):
                            cls, confi, coordi = res[i]

                            # while cls identified is other than safe
                            if cls.decode() != 'safe':
                                xmi, ymi, xma, yma = bbox2points(coordi)

                                # OVERLAP CALCULATION on DETECTED RESULTS
                                overlap = overlap_red_markup_v2(coordi_dict=lst_markup_coord,
                                                                min_x=xmi, min_y=ymi,
                                                                max_x=xma, max_y=yma)
                                if overlap:
                                    any_overlapping += 1
                                result.append((cls, confi, (xmi, ymi), (xma, yma)))

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
                            cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/'+str(ctr)+'_fgd.jpg', fgmask)
                            cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/' + str(ctr) + '_det.jpg', image_)
                            ctr+=1
                            save_detect_path = dir_of_file + '/ship/reference_files/detect_' + str(cam_) + '.jpg'
                            cv2.imwrite(save_detect_path, image_)
                            notification_trigger(cameraID=cam_, object='Vessel', status='Threat',
                                                 object_known=cls.decode(), image_path=save_detect_path)

                        # NOTIFICATION for DETECTION but, NO OVERLAPPING Scenario
                        else:
                            # Finding CONTOUR on BW Masked Image
                            contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                            draw = 0
                            # Area of Contour
                            for contour in contours:
                                area = cv2.contourArea(contour)
                                if 40 < area < 5000:
                                    cv2.drawContours(image_, contour, -1, (200, 4, 14), 1)
                                    draw += 1
                            if draw > 0 or image_ is not None:
                                curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                                save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_' + str(cam_) + '_' + curr_time + '.jpg'
                                cv2.imwrite(save_unknown_path, image_)
                                cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/' + str(ctr) + '_fgdn.jpg',fgmask)
                                cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/' + str(ctr) + '_detn.jpg',image_)
                                ctr += 1

                                # NOTIFICATION TRIGGER for Unknown Detection +
                                # Threat Detections + No Overlap
                                notification_trigger(cameraID=cam_,
                                                     object='Vessel_No_breach',
                                                     status=cls.decode(),
                                                     object_known='Known',
                                                     image_path=save_unknown_path)

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
                            if 40 < area < 5000:
                                cv2.drawContours(image_, contours, -1, (191, 11, 11), 2)
                                draw += 1
                        if draw > 0:
                            curr_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
                            save_unknown_path = dir_of_file + '/ship/unknown_objects/unk_' + str(cam_) + '_' + curr_time + '.jpg'
                            cv2.imwrite(save_unknown_path, image_)
                            #cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/' + str(ctr) + '_fgd.jpg',fgmask)
                            cv2.imwrite('D:/darknet_fender_protection/ship/paper_iamges/' + str(ctr) + '_det.jpg',image_)
                            ctr += 1

                            # NOTIFICATION TRIGGER for Unknown Detection + No Detections
                            notification_trigger(cameraID=cam_, object='Unidentified Object',
                                                 status='System not Trained',
                                                 object_known='UnKnown',
                                                 image_path=save_unknown_path)
                    #else:
                    #    pass

                # if Frame is not Read
                else:
                    if start_timer == 0:
                        # start timer if Frame not Recieved
                        start_timer = time.time()
                    # check if timer is active for 120 sec or 2 mins
                    if start_timer != 0 and time.time() - start_timer > 60:
                        active_cams.remove(cam_)            # delete cameraID from Active cam list
                        del VLC_PLAYER_OBJECT[cam_]         # del VLC object of cameraID
                        restart_status = True               # Status : True to reacquire objects for camID
                        camera_status_notification(cam_id=cam_, status_code=0)      # notification trigger to add
                        print('failed request sent for CAMID : ', cam_)

