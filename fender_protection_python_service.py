import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import threading_main  as thpy
from interface_manager_v3 import *
import threading



class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "fender_protection_service_python"
    _svc_display_name_ = "fender_protection_service_python"


    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        pass

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                          servicemanager.PYS_SERVICE_STARTED,
                          (self._svc_name_,''))
        self.main()

    def main(self):
        e = '5'
        main_program(e, all_camera_data[e])


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)