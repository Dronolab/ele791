
import time

import GeneralSettings
from Gpio import Gpio
from processAbstract import ProcessAbstract


class Trigger(ProcessAbstract):
    GPIO_PIN = GeneralSettings.TRIGGERGPIOPIN
    DEFAULT_VALUE = 0;
    TRIGGER_TIME = 0.3 #(500 ms)
    TRIGGER_WAIT = 0.8
    def __init__(self):
        ProcessAbstract.__init__(self)
        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "out")
            self.__gpio.writepin(self.DEFAULT_VALUE)


    def _process(self):
        print("trigger process")
        while not self._kill:
            if not GeneralSettings.FAKEIO:

                self.__gpio.writepin(1)
                self.addTimeToQueue(time.time())
                time.sleep(self.TRIGGER_TIME)
                self.__gpio.writepin(0)
                time.sleep(self.TRIGGER_WAIT)
            else:
                print("in fakeio")
                time.sleep(1)
                f = open("val","w")
                f.write(str(0))
                f.close()
                time.sleep(0.01)
                f = open("val", "w")
                f.write(str(1))
                f.close()
                print("trigerring")
                self.addTimeToQueue(time.time())
        self.__gpio.writepin(self.DEFAULT_VALUE)