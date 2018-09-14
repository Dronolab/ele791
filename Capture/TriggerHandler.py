import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


import time
from abc import abstractmethod

from Utility.ZmqUtility.MsgDefinition import TriggerAction, TakePicture

import GeneralSettings
from .Gpio import triggerGPIO, Gpio
from Utility.ZmqUtility import zmqSocket
from Utility.processAbstract import ProcessAbstract


class TriggerHandler(ProcessAbstract):
    GPIO_PIN = GeneralSettings.TRIGGERGPIOPIN
    GPIO_DEFAULT_VALUE = 0;
    GPIO_TRIGGER_ON = 1
    TRIGGER_TIME = 0.3 #(500 ms)
    TRIGGER_WAIT = 0.8
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"

    def __init__(self,time_queue):
        ProcessAbstract.__init__(self)
        self.__time_queue = time_queue

        if not GeneralSettings.FAKEIO:
            self.__gpio = Gpio(self.GPIO_PIN, "out")
            self.__gpio.writepin(self.GPIO_DEFAULT_VALUE)


    def _process(self):
        print("trigger process")
        self.__listen_socket = zmqSocket.createSubSocket(TakePicture.TOPIC)
        while self._kill_pill.empty():
            try:
                if not GeneralSettings.FAKEIO:
                    msg = zmqSocket.subReadMsg(self.__listen_socket)
                    print("Single Trigger")
                    st = SingleTrigger(self.GPIO_PIN, self.__time_queue)
                    st.capture()

                else:
                    st = FakeSingleTrigger(self.__time_queue)
                    st.capture()
                    self.__time_queue.put(time.time())
            except KeyboardInterrupt:
                st = FakeSingleTrigger(self.__time_queue)
                st.trigger_off()
                self.softProcessStop()

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
        BaseTrigger.__init__(self,queue)
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
    TRIGGER_TIME = 0.5
    TRIGGER_WAIT = 0.6
    TRIGGER_ON_TOPIC = "trigger_on"
    TRIGGER_OFF_TOPIC = "trigger_off"
    GPIO_TRIG_ON = 1
    GPIO_TRIG_OFF = 0

    def __init__(self,GPIO_PIN):
        BaseTrigger.__init__(self,None)

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
