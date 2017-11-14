
import time

import GeneralSettings
from Gpio import Gpio
from processAbstract import ProcessAbstract
import ZmqSocket

class Trigger(ProcessAbstract):
    GPIO_PIN = GeneralSettings.TRIGGERGPIOPIN
    DEFAULT_VALUE = 0;
    TRIGGER_TIME = 0.3 #(500 ms)
    TRIGGER_WAIT = 0.8
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"

    def __init__(self):
        ProcessAbstract.__init__(self)

        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "out")
            self.__gpio.writepin(self.DEFAULT_VALUE)




    def _process(self):
        print("trigger process")
        self._pubSocket = ZmqSocket.createPubSocket()
        while not self._kill:
            if not GeneralSettings.FAKEIO:

                self.__gpio.writepin(1)
                current = time.time()
                self.addTimeToQueue(current)
                ZmqSocket.publishMsg(self._pubSocket, self.TRIGGER_ON_TOPIC, current)

                time.sleep(self.TRIGGER_TIME)
                self.__gpio.writepin(0)
                ZmqSocket.publishMsg(self._pubSocket, self.TRIGGER_OFF_TOPIC, time.time())
                time.sleep(self.TRIGGER_WAIT)
            else:
                print("in fakeio")
                time.sleep(1)
                f = open("val","w")
                f.write(str(0))
                current = time.time()
                f.close()
                ZmqSocket.publishMsg(self._pubSocket, self.TRIGGER_ON_TOPIC, current)
                time.sleep(0.01)
                f = open("val", "w")
                f.write(str(1))
                f.close()
                print("trigerring")
                ZmqSocket.publishMsg(self._pubSocket, self.TRIGGER_OFF_TOPIC, time.time())
                self.addTimeToQueue(current)
        self.__gpio.writepin(self.DEFAULT_VALUE)