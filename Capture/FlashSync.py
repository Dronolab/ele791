import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time

from Utility.ZmqUtility.MsgDefinition import PictureTaken

import GeneralSettings
from .Gpio import Gpio
from Utility.ZmqUtility import zmqSocket
from Utility.processAbstract import ProcessAbstract


class FlashSync(ProcessAbstract):
    PULL_INTERVAL = 0.005 # pull interval for flash in s
    DEFAULT_VAUE = 1
    GPIO_PIN = GeneralSettings.FLASHGPIOPIN
    FLASHLATENCY = 0.06
    FLASH_TOPIC = "flash_detected"

    def __init__(self, time_queue):
        self.__time_queue = time_queue
        ProcessAbstract.__init__(self)
        print("Flash init")
        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "in")

    def notifyPictureTaken(self, unix_time):
        self.__time_queue.put(unix_time)
        msgClass = PictureTaken()
        msgClass.setCaptureTime(unix_time)
        zmqSocket.publishMsg(self._pubSocket, msgClass.generateMsg())

    def _process(self):
        self._pubSocket = zmqSocket.createPubSocket()
        last_value = self.DEFAULT_VAUE

        # need a rework
        if not GeneralSettings.FAKEIO:
            f = open(self.__gpio.getFileName(), "r")

        else:
            f = open("val", "r")
        while self._kill_pill.empty():
            try:
                if not GeneralSettings.FAKEIO:
                    f.seek(0)
                    val = (f.read(1))
                    val = int(val)
                    # print(val)
                    if last_value == 1 and val == 0: # falling edge detection
                        current = (time.time() - self.FLASHLATENCY)
                        self.notifyPictureTaken(current)

                    last_value = val
                    time.sleep(self.PULL_INTERVAL)

                else:

                    self.notifyPictureTaken(time.time())
                    time.sleep(1)
            except KeyboardInterrupt:
                self.softProcessStop()

        f.close()