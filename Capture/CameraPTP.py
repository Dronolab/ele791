import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from Utility.ZmqUtility.MsgDefinition import PictureDownloaded

import GeneralSettings
from GeneralSettings import logger
from Utility.ZmqUtility import zmqSocket
from Utility.processAbstract import ProcessAbstract
from .Gpio import cameraAlimGPIO

if not GeneralSettings.FAKEIO:
    from .SonyA6000 import ptpCamera

class Camera(ProcessAbstract):
    EVENT_NEW_PICTURE_TOPIC = "picture_downloaded"

    def __init__(self,time_queue):
        ProcessAbstract.__init__(self)
        self.__time_queue = time_queue
        self.cam_alim = cameraAlimGPIO()
        self.cam_alim.unpower_camera()
        time.sleep(2)
        self.cam_alim.power_camera()
        if not GeneralSettings.FAKEIO :
            # self.__ptpCamera = ptpCamera()
            pass

    def notifyPictureDownloaded(self,unix,file_path):
        msgClass = PictureDownloaded()
        msgClass.setDownloadTime(unix)
        msgClass.setFilePath(file_path)
        self.__time_queue.put(unix)
        zmqSocket.publishMsg(self._pubSocket, msgClass.generateMsg())


    def _process(self):
        self._pubSocket = zmqSocket.createPubSocket()
        logger.debug("Starting loop")
        while self._kill_pill.empty():
            try:
                self.__ptpCamera = ptpCamera()
                if not GeneralSettings.FAKEIO:

                    event = self.__ptpCamera.watch_event(500)
                    # print(event)
                    if not event:
                        continue
                    # print(self.__ptpCamera.list_files())
                    if (self.__ptpCamera.getEventType(event) == self.__ptpCamera.EVENT_FILE_ADDED):
                        curent = time.time()
                        print("new file added")
                        picture_path =self.__ptpCamera.downloadPictureFromEvent(event)
                        self.notifyPictureDownloaded(curent, picture_path)

                else :
                    time.sleep(1)
                    curent = time.time()
                    self.notifyPictureDownloaded(curent, None)
            except KeyboardInterrupt:
                self.softProcessStop()


            self.__ptpCamera.__del__()
            self.cam_alim.unpower_camera()