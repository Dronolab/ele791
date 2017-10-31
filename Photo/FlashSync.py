import time
from multiprocessing import Process , Queue, Lock
from processAbstract import ProcessAbstract

class FlashSync(ProcessAbstract):
    PULL_INTERVAL = 0.005 # pull interval for flash in s
    DEFAULT_VAUE = 1
    GPIO_PIN = 398

    def __init__(self):
        ProcessAbstract.__init__(self)
        print("GPIO_PIN")
        self.GPIO_pin = self.GPIO_PIN

    def getFlashTime(self):
        return self.qetTimeFromQueue()


    def _process(self):
        last_value = self.DEFAULT_VAUE
        f = open("val", "r")
        print(f.read(1))
        while not self._kill:
            with self._process_lock:
                f.seek(0)
                print("hello")
                val = int(f.read(1))
                if last_value == 1 and val == 0: # falling edge detection
                    self.addTimeToQueue(time.time())
                last_value = val
                time.sleep(self.PULL_INTERVAL)
        f.close()