from multiprocessing import Queue, Process, Lock
import time
from processAbstract import ProcessAbstract
from SonyA6000 import ptpCamera

class Camera(ProcessAbstract):
    def __init__(self):
        ProcessAbstract.__init__(self)
        self.__ptpCamera = ptpCamera()

    def _process(self):
        while not self._kill:
            print("Event loop")
            event = self.__ptpCamera.watch_event()

            self.addTimeToQueue(time.time())


