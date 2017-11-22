
import time
from abc import abstractmethod

import GeneralSettings
from Gpio import triggerGPIO, Gpio
from ZmqUtility import zmqSocket
from processAbstract import ProcessAbstract


class TriggerHandler(ProcessAbstract):
    GPIO_PIN = GeneralSettings.TRIGGERGPIOPIN
    GPIO_DEFAULT_VALUE = 0;
    GPIO_TRIGGER_ON = 1
    TRIGGER_TIME = 0.3 #(500 ms)
    TRIGGER_WAIT = 0.8
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"

    def __init__(self):
        ProcessAbstract.__init__(self)

        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "out")
            self.__gpio.writepin(self.GPIO_DEFAULT_VALUE)


    def _process(self):
        print("trigger process")
        self._pubSocket = zmqSocket.createPubSocket()
        while not self._kill:
            if not GeneralSettings.FAKEIO:
                st = SingleTrigger()
                st.capture()

            else:
                st = FakeSingleTrigger()
                st.capture()
                self.addTimeToQueue(time.time())

        if not GeneralSettings.FAKEIO:
            self.__gpio.writepin(self.GPIO_DEFAULT_VALUE)

def getTriggerClass(triggerConstructer):
    pass

class triggerConstructor:
    def __init__(self,capture_Type, fake_IO):

        pass

class BaseTrigger():
    def __init__(self):
        self.nb_capture = 0
        self.nb_capture_left = 0

    @abstractmethod
    def trigger_on(self):
        pass
    @abstractmethod
    def trigger_off(self):
        pass

    @abstractmethod
    def capture(self):
        pass

class SingleTrigger(BaseTrigger):
    TRIGGER_TIME = 0.3
    TRIGGER_WAIT = 0.8
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"
    GPIO_TRIG_ON = 1
    GPIO_TRIG_OFF = 0

    def __init__(self,GPIO_PIN):
        BaseTrigger.__init__()
        self.triggerGpio = triggerGPIO()
        self.zmqPubSocket = zmqSocket.createPubSocket()


    def trigger_on(self):
        self.triggerGpio.activatePin()
        current = time.time()
        zmqSocket.publishMsg(self.zmqPubSocket, self.TRIGGER_ON_TOPIC, current) # to be modify
        time.sleep(self.TRIGGER_TIME)

    def trigger_off(self):
        self.triggerGpio.unActivatePin()
        zmqSocket.publishMsg(self.zmqPubSocket, self.TRIGGER_OFF_TOPIC, time.time())
        time.sleep(self.TRIGGER_WAIT)

    def capture(self, loop = False, nb_cap_todo = 1):
        self.nb_capture_left = self.nb_capture_left + nb_cap_todo
        while self.nb_capture_left > 0:
            self.trigger_on()
            self.trigger_off()
            self.nb_capture_left -= 1
            self.nb_capture = 1
            if not loop:
                break



class FakeSingleTrigger(BaseTrigger):
    TRIGGER_TIME = 0.3
    TRIGGER_WAIT = 0.8
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"
    GPIO_TRIG_ON = 1
    GPIO_TRIG_OFF = 0

    def __init__(self,GPIO_PIN):
        BaseTrigger.__init__()
        self.zmqPubSocket = zmqSocket.createPubSocket()


    def trigger_on(self):
        f = open("val", "w")
        f.write(str(self.GPIO_TRIG_ON))
        f.close()
        current = time.time()
        zmqSocket.publishMsg(self.zmqPubSocket, self.TRIGGER_ON_TOPIC, current) # to be modify
        time.sleep(self.TRIGGER_TIME)

    def trigger_off(self):
        f = open("val", "w")
        f.write(str(self.GPIO_TRIG_OFF))
        f.close()
        zmqSocket.publishMsg(self.zmqPubSocket, self.TRIGGER_OFF_TOPIC, time.time())
        time.sleep(self.TRIGGER_WAIT)

    def capture(self, loop = False, nb_cap_todo = 1):
        self.nb_capture_left = self.nb_capture_left + nb_cap_todo
        while self.nb_capture_left > 0:
            self.trigger_on()
            self.trigger_off()
            self.nb_capture_left -= 1
            self.nb_capture = 1
            if not loop:
                break
