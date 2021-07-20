from interface_manager_v3 import *
import threading

while True:
    thread = []

    try:
        for e in all_camera_data.keys():
            thread.append(threading.Thread(target=main_program, args=(e, all_camera_data[e])))
            thread[-1].start()
            time.sleep(2)

        for item in thread:
            item.join()

    except:
        print('Inside Threading Except')
        all_camera_data = []
        VLC_PLAYER_OBJECT = {}
        gc.collect()



    # --------------------- FOR TESTING ONLY ------------

    """
    if __name__ == '__main__':
        e = '5'
        main_program(e, all_camera_data[e])
    
    #"""
