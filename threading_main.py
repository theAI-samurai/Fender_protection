from main import *
import threading

threads_opened = []

for cams in active_cameras:
    threads_opened.append(threading.Thread(target=main_program, args=(cams,)))
    threads_opened[-1].start()


for t in threads_opened:
    t.join()







