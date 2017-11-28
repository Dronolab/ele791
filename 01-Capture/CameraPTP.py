import time

import GeneralSettings
from ZmqUtility import zmqSocket
from ZmqUtility.MsgDefinition import PictureDownloaded
from processAbstract import ProcessAbstract

if not GeneralSettings.FAKEIO:
    from SonyA6000 import ptpCamera

class Camera(ProcessAbstract):
    EVENT_NEW_PICTURE_TOPIC = "picture_downloaded"
    def __init__(self):
        ProcessAbstract.__init__(self)

        if not GeneralSettings.FAKEIO :
            self.__ptpCamera = ptpCamera()

    def notifyPictureDownloaded(self,unix,file_path):
        msgClass = PictureDownloaded()
        msgClass.setDownloadTime(unix)
        msgClass.setFilePath(file_path)

        self.addTimeToQueue(unix)
        zmqSocket.publishMsg(self._pubSocket, msgClass.generateMsg())

    def _process(self):
        self._pubSocket = zmqSocket.createPubSocket()
        while not self._kill:

            if not GeneralSettings.FAKEIO:
                    event = self.__ptpCamera.watch_event()
                    if (self.__ptpCamera.getEventType(event) == self.__ptpCamera.EVENT_FILE_ADDED):
                        curent = time.time()
                        picture_path =self.__ptpCamera.downloadPictureFromEvent(event)
                        self.notifyPictureDownloaded(curent, picture_path)
                        print("new file added")

            else :
                time.sleep(1)
                curent = time.time()
                self.notifyPictureDownloaded(curent, None)

