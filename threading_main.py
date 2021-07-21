from interface_manager_v3 import *
import threading


thread = []

#''''
for e in all_camera_data.keys():
    # thread.append(threading.Thread(target=main_program, args=(e, all_camera_data[e])))
    # thread[-1].start()
    x = threading.Thread(target=main_program, args=(e, all_camera_data[e]))
    x.start()
    time.sleep(1)

for item in thread:
    item.join()
# '''


# --------------------- FOR TESTING ONLY ------------

"""
if __name__ == '__main__':
    e = '5'
    main_program(e, all_camera_data[e])

#"""
