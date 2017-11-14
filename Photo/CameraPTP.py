import time
from processAbstract import ProcessAbstract


import time

import GeneralSettings
from processAbstract import ProcessAbstract

if not GeneralSettings.FAKEIO:
    from SonyA6000 import ptpCamera

class Camera(ProcessAbstract):
    def __init__(self):
        ProcessAbstract.__init__(self)
        if not GeneralSettings.FAKEIO :
            self.__ptpCamera = ptpCamera()

    def _process(self):
        while not self._kill:

            if not GeneralSettings.FAKEIO:
                    event = self.__ptpCamera.watch_event()
                    if (self.__ptpCamera.getEventType(event) == self.__ptpCamera.EVENT_FILE_ADDED):
                        self.addTimeToQueue(time.time())
                        self.__ptpCamera.downloadPictureFromEvent(event)
                        print("new file added")
                    print("helllo")
            else :
                time.sleep(1)
                self.addTimeToQueue(time.time())

