from read_config import *
from image_codes import *

stream1 = 'rtsp://192.168.29.73:8554/vlc'
stream2 = 'rtsp://admin:DS-2CD206@192.168.29.32'

# Method 1 ---- using OPENCV
cap = cv2.VideoCapture(stream2, cv2.CAP_FFMPEG)
ctr = 0
print(cap)
while True and ctr < 20:
    print(cap.isOpened())
    ret, frame = cap.read()
    print(ret, type(frame))
    ctr = ctr+1


# Method 2  --------> using vlc
vlc_player_object = vlc.MediaPlayer(stream1)
time.sleep(4)
vlc_player_object.play()
ctr = 0
while (True and ctr<20) or (vlc_player_object.is_playing() and ctr<50):
    print(vlc_player_object.is_playing())
    print(ctr)
    time.sleep(1)
    vlc_player_object.video_take_snapshot(0, 'D:/my_repos/darknet_fender_protection/vlc_stream.jpg', 0, 0)
    ctr = ctr +1
vlc_player_object.stop()
vlc_player_object.release()
del vlc_player_object

# Method 3 --------> using rtsp

