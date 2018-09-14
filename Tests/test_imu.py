import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

# from UavInteraction.UavMavlinkHandler import mavlinkHandler
from Geotag.imuHandler import ImuHandler
from Utility.ZmqUtility.zmqBroker import Broker

from multiprocessing import Queue
import time
from Geotag.geotagPhoto import geotagPhoto


if __name__ == '__main__':

    q = Queue()

    broker = Broker()
    broker.start()


    imu = ImuHandler(q)
    imu.start()

    while True:
        try:
            time.sleep(0.05)
            imu=q.get()
            print("%f %f %f" %(imu.pitch,imu.roll,imu.yaw))
        except KeyboardInterrupt:
            break