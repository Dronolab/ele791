import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from multiprocessing import Queue
from Utility.ZmqUtility.zmqBroker import Broker
import time

from Capture.FlashSync import FlashSync


if __name__ == '__main__':

    flash_t_queue = Queue()

    broker = Broker()
    flash = FlashSync(flash_t_queue)

    broker.start()
    flash.start()

    time.sleep(30)
    print(flash_t_queue.qsize())