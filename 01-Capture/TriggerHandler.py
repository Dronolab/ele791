
import time
from abc import abstractmethod

import GeneralSettings
from Gpio import triggerGPIO, Gpio
from ZmqUtility import zmqSocket
from ZmqUtility.MsgDefinition import TriggerAction
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
        while not self._kill:
            if not GeneralSettings.FAKEIO:
                st = SingleTrigger(self.__timeQueue)
                st.capture()

            else:
                st = FakeSingleTrigger(self._timeQueue)
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
    def __init__(self,queue):
        self.nb_capture = 0
        self.nb_capture_left = 0
        self.zmqPubSocket = zmqSocket.createPubSocket()
        self.timeQueue = queue

    @abstractmethod
    def trigger_on(self):
        pass
    @abstractmethod
    def trigger_off(self):
        pass

    @abstractmethod
    def capture(self):
        pass

    def pubNotifyTriggre(self,msgClass):
        zmqSocket.publishMsg(self.zmqPubSocket, msgClass.generateMsg())

    def notifyTriggerOn(self):
        current = time.time()
        msgClass = TriggerAction()
        msgClass.setUnixTime(current)
        msgClass.setActionType("on")
        self.pubNotifyTriggre(msgClass)


    def notifyTriggerOff(self):
        current = time.time()
        msgClass = TriggerAction()
        msgClass.setUnixTime(current)
        msgClass.setActionType("on")
        self.pubNotifyTriggre(msgClass)



class SingleTrigger(BaseTrigger):
    TRIGGER_TIME = 0.3
    TRIGGER_WAIT = 0.8
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"
    GPIO_TRIG_ON = 1
    GPIO_TRIG_OFF = 0

    def __init__(self,GPIO_PIN,queue):
        BaseTrigger.__init__(queue)
        self.triggerGpio = triggerGPIO()

    def trigger_on(self):
        self.triggerGpio.activatePin()
        self.notifyTriggerOn()
        time.sleep(self.TRIGGER_TIME)

    def trigger_off(self):
        self.triggerGpio.unActivatePin()
        self.notifyTriggerOff()
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

    def trigger_on(self):
        f = open("val", "w")
        f.write(str(self.GPIO_TRIG_ON))
        f.close()
        self.notifyTriggerOn()
        time.sleep(self.TRIGGER_TIME)

    def trigger_off(self):
        f = open("val", "w")
        f.write(str(self.GPIO_TRIG_OFF))
        f.close()
        self.notifyTriggerOff()
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
