
from data_validate import *
from requests_handling import *
from darknet import *
from image_codes import *
import math


VLC_PLAYER_OBJECT = {}

# validate Active Streams
active_cameras, inactive_cameras = active_streams_initialize_vlc(all_camera_data)     # list of active camera ids

print('-------------ACTIVE--------', active_cameras)

# vlc_payer_object creation for active cameras
for act_cam_id in active_cameras:
    temp_obj = vlc_stream_object_init_2(cam_id=act_cam_id, conf_cam_data=all_camera_data)
    VLC_PLAYER_OBJECT.update({act_cam_id: temp_obj})
    del temp_obj

# model_initialize
net = model_load(cfgPath=dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                 wgtPath=dir_of_file + '/ship/cfg/yolov3_full_ship_2000.weights')

# loading Deeplearning model

obj_detect = ObjectDetection(dataPath=dir_of_file + '/ship/cfg/ship.data', netwrk=net, camID=0)


def main_program(cam_):
    fender_image, minx, miny, maxx, maxy = fender_coordi(path_=dir_of_file+'/ship/reference_files/markup_'+(cam_)+'.jpg')
    while True:
        read = read_frames_using_vlc(player=VLC_PLAYER_OBJECT[cam_],  delay_time=1,
                                     cam_id=cam_, base_path=dir_of_file+'/ship/reference_files/')
        if read:
            frame_path = dir_of_file+'/ship/reference_files/'+str(cam_)+'.jpg'              # frame path
            markup_img_pa = dir_of_file+'/ship/reference_files/markup_'+str(cam_)+'.jpg'    # markup_path
            new_dim = height_width_validate(markup_img_pa, markup_img_pa)
            markup_img = cv2.resize(cv2.imread(markup_img_pa), new_dim)                     # Read markup image
            lst_markup_coord = list_marking_coord(markup_img)                               # List of Markup Coord
            res = obj_detect.detect(frame_path.encode('ascii'))   # calling detection on the saved snapshot
            for i in range(len(res)):
                cls, confi, coordi = res[i]
                if cls == b'boat':
                    xmi, ymi, xma, yma = bbox2points(coordi)        # coordinate of object in image
                    # overlap = check_for_overlap(xmi, ymi, xma, yma, minx, miny, maxx, maxy)
                    overlap = overlap_from_left_red_markup(cord_lst=lst_markup_coord, top_right=(xma, ymi))
                    if overlap:
                        image = cv2.resize(cv2.imread(frame_path), new_dim)               # snapshot image file read
                        image = cv2.rectangle(image, (math.floor(xmi), math.floor(ymi)), (math.floor(xma), math.floor(yma)), (255, 255, 0), 2)
                        image = cv2.rectangle(image, (minx, miny), (maxx, maxy), (0, 0, 0), 2)
                        image_ = cv2.addWeighted(image, 1, markup_img, 1, 0)
                        save_detect_path = dir_of_file+'/ship/reference_files/detect_'+str(cam_)+'.jpg'
                        cv2.imwrite(save_detect_path, image_)
                        time.sleep(2)
                        notification_trigger(cameraID=cam_, object=cls, status='Threat',
                                             object_known='Known',image_path=save_detect_path)
        else:
            #thread sleep
            #thime
            pass


