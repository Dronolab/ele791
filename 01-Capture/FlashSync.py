import time

import GeneralSettings
from Gpio import Gpio
from ZmqUtility import zmqSocket
from ZmqUtility.MsgDefinition import PictureTaken
from processAbstract import ProcessAbstract


class FlashSync(ProcessAbstract):
    PULL_INTERVAL = 0.005 # pull interval for flash in s
    DEFAULT_VAUE = 1
    GPIO_PIN = GeneralSettings.FLASHGPIOPIN
    FLASHLATENCY = 0.06
    FLASH_TOPIC = "flash_detected"

    def __init__(self):
        ProcessAbstract.__init__(self)
        print("GPIO_PIN")

        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "in")

    def getFlashTime(self):
        return self.qetTimeFromQueue()


    def notifyPictureTaken(self, unix_time):
        self.addTimeToQueue(unix_time)
        msgClass = PictureTaken()
        msgClass.setCaptureTime(unix_time)
        zmqSocket.publishMsg(self._pubSocket, msgClass.generateMsg())

    def _process(self):
        self._pubSocket = zmqSocket.createPubSocket()
        last_value = self.DEFAULT_VAUE

        # need a rework
        if not GeneralSettings.FAKEIO:
            print(self.__gpio.getFileName())
            f = open(self.__gpio.getFileName(), "r")

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
                        current = (time.time() -self.FLASHLATENCY)
                        self.notifyPictureTaken(current)

                    last_value = val
                    if val == 0 :
                        print(val)
                    time.sleep(self.PULL_INTERVAL)

                else:
                    self.notifyPictureTaken(time.time())
                    time.sleep(1)

        f.close()