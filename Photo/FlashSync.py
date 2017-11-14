import time

import GeneralSettings
from Gpio import Gpio
from processAbstract import ProcessAbstract


class FlashSync(ProcessAbstract):
    PULL_INTERVAL = 0.005 # pull interval for flash in s
    DEFAULT_VAUE = 1
    GPIO_PIN = GeneralSettings.FLASHGPIOPIN
    FLASHLATENCY = 0.06

    def __init__(self):
        ProcessAbstract.__init__(self)
        print("GPIO_PIN")
        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "in")

    def getFlashTime(self):
        return self.qetTimeFromQueue()


    def _process(self):
        last_value = self.DEFAULT_VAUE
        if not GeneralSettings.FAKEIO:
            print(self.__gpio.getFileName())
            f = open(self.__gpio.getFileName(), "r")
            print("asdasDASDSADSAD")
        else:
            f = open("val", "r")

        while not self._kill:
            with self._process_lock:
                if not GeneralSettings.FAKEIO:
                    f.seek(0)
                    val = (f.read(1))
                    val = int(val)
                    # print(val)
                    if last_value == 1 and val == 0: # falling edge detection
                        self.addTimeToQueue(time.time()- self.FLASHLATENCY)
                    last_value = val
                    if val == 0 :
                        print(val)
                    time.sleep(self.PULL_INTERVAL)
                else:
                    self.addTimeToQueue(time.time())
                    time.sleep(1)

        f.close()