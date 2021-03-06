from read_config import *
from data_validate import *
from requests_handling import *
from darknet import *
from image_codes import *
import math

vlc_player_object = {}

# validate Active Streams
active_cameras = active_streams_initialize_vlc(all_camera_data)     # list of active camera ids

# get markup and snapshot images for active cameras
for id in active_cameras:
    get_markup_image(id)
    get_reference_snapshot_image(id)


# loading Deeplearning model
obj_detect = ObjectDetection(dir_of_file + '/ship/cfg/yolov3_full_ship.cfg',
                             dir_of_file + '/ship/cfg/yolov3_full_ship_2000.weights',
                             dir_of_file + '/ship/cfg/ship.data'
                             )
cam = ['3']         # ----------> setting this for Testing pourpose only

for cam_ in cam:   # active_cameras:
    vlc_player_object.update({cam_: vlc.MediaPlayer(all_camera_data[cam_])})

for cam_ in cam:    # active_cameras:
    fender_image, minx, miny, maxx, maxy = fender_coordi(dir_of_file+'/ship/reference_files/markup_'+(cam_)+'.jpg')
    # fender_image = cv2.circle(fender_image, (minx,miny), radius=5, color=(255, 0, 255), thickness=3)

    while True:
        read = read_frames_using_vlc(player=vlc_player_object[cam_],  delay_time=1,
                              cam_id=cam_, base_path=dir_of_file+'/ship/reference_files/')
        # print(read)
        if read:
            frame_path = dir_of_file+'/ship/reference_files/'+str(cam_)+'.jpg'

            res = obj_detect.detect(frame_path.encode('ascii'))
            for i in range(len(res)):
                cls, confi, coordi = res[i]
                if cls == b'boat':
                    xmi, ymi, xma, yma = bbox2points(coordi)
                    overlap = check_for_overlap(xmi, ymi, xma, yma, minx, miny, maxx, maxy)
                    image = cv2.imread(frame_path)
                    image = cv2.rectangle(image, (math.floor(xmi), math.floor(ymi)), (math.floor(xma), math.floor(yma)),(255, 255, 0), 2)
                    image = cv2.rectangle(image,(minx,miny),(maxx,maxy),(0,0,0),2)
                    cv2.imshow('winname', image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    if overlap:
                        notification_trigger(cameraID=cam_, object=cls, status='Threat',
                                             object_known='Known',image_path= frame_path)
                    else:
                        print('Nothing detected')

