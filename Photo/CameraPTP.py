from multiprocessing import Queue, Process, Lock
import time
from processAbstract import ProcessAbstract

class Camera(ProcessAbstract):
    def __init__(self):
        ProcessAbstract.__init__(self)

    def _process(self):
        print("Event loop")
        self.addTimeToQueue(time.time())
        time.sleep(1)

