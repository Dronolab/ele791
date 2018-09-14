import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

# from UavInteraction.UavMavlinkHandler import mavlinkHandler
from Capture.CameraPTP import Camera
from Utility.ZmqUtility.zmqBroker import Broker

from multiprocessing import Queue
import time
from Geotag.geotagPhoto import geotagPhoto


q = Queue()

broker = Broker()
broker.start()

cam = Camera(q)
cam.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
print(q.qsize())