from multiprocessing import Queue, Process
import time
from processAbstract import ProcessAbstract
class Trigger(ProcessAbstract):
    GPIO_PIN = 389
    TRIGGER_TIME = 0.5 #(500 ms)
    def __init__(self):
        ProcessAbstract.__init__(self)


    def _process(self):
        while not self._kill:
            print("add trigger here")
            self.addTimeToQueue(time.time())
            time.sleep(self.TRIGGER_TIME)
            print("remove trigger")
