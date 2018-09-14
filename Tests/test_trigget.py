import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import time
from multiprocessing import Queue

from Capture.CameraPTP import Camera
from Utility.ZmqUtility.zmqBroker import Broker
from Capture.TriggerHandler import  TriggerHandler






if __name__ == '__main__':

    trigger_t_queue = Queue()

    trigger = TriggerHandler(trigger_t_queue)
    trigger.start()

    time.sleep(30)
    print(trigger_t_queue.qsize())