import time

import GeneralSettings
from ZmqUtility import zmqSocket
from processAbstract import ProcessAbstract

if not GeneralSettings.FAKEIO:
    from SonyA6000 import ptpCamera

class Camera(ProcessAbstract):
    EVENT_NEW_PICTURE_TOPIC = "picture_downloaded"
    def __init__(self):
        ProcessAbstract.__init__(self)

        if not GeneralSettings.FAKEIO :
            self.__ptpCamera = ptpCamera()

    def _process(self):
        self._pubSocket = zmqSocket.createPubSocket()
        while not self._kill:

            if not GeneralSettings.FAKEIO:
                    event = self.__ptpCamera.watch_event()
                    if (self.__ptpCamera.getEventType(event) == self.__ptpCamera.EVENT_FILE_ADDED):
                        curent = time.time()
                        self.addTimeToQueue(curent)
                        self.__ptpCamera.downloadPictureFromEvent(event)
                        msg = curent
                        zmqSocket.publishMsg(self._pubSocket, self.EVENT_NEW_PICTURE_TOPIC, msg)
                        print("new file added")
                    print("helllo")
            else :
                time.sleep(1)
                self.addTimeToQueue(time.time())
                msg = time.time()
                zmqSocket.publishMsg(self._pubSocket, self.EVENT_NEW_PICTURE_TOPIC, msg)

