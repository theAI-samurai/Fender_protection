from interface_manager import *
import threading

thread = []

# '''
for e in all_camera_data.keys():
    thread.append(threading.Thread(target=main_program, args=(e, all_camera_data[e])))
    thread[-1].start()

for item in thread:
    item.join()
# '''


