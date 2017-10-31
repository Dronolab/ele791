
import time
from processAbstract import ProcessAbstract
from Gpio import Gpio

class Trigger(ProcessAbstract):
    GPIO_PIN = 389
    TRIGGER_TIME = 0.5 #(500 ms)
    def __init__(self):
        ProcessAbstract.__init__(self)
        self.gpio = Gpio(self.GPIO_PIN, "out")


    def _process(self):
        while not self._kill:
            self.gpio.writepin(1)
            self.addTimeToQueue(time.time())
            time.sleep(self.TRIGGER_TIME)
            self.gpio.writepin(0)
