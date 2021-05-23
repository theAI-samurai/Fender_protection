from interface_manager_v3 import *
import threading

thread = []

'''
for e in all_camera_data.keys():
    thread.append(threading.Thread(target=main_program, args=(e, all_camera_data[e])))
    thread[-1].start()

for item in thread:
    item.join()
# '''


# --------------------- FOR TESTING ONLY ------------
#"""

if __name__ == '__main__':
    e = '9'
    main_program(e, all_camera_data[e])

#"""
