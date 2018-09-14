import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import time
from multiprocessing import Queue

import GeneralSettings
from Capture.CameraPTP import Camera
from Utility.ZmqUtility.zmqBroker import Broker
from Capture.FlashSync import FlashSync
from Capture.TriggerHandler import TriggerHandler
from Capture.photoSync import PhotoSync
from Geotag.imuHandler import ImuHandler

from UavInteraction.UavMavlinkHandler import mavlinkHandler


if __name__ == '__main__':

    flash_t_queue = Queue()
    cam_t_queue = Queue()
    trigger_t_queue = Queue()
    gps_data = Queue()
    imu_queue = Queue()

    broker = Broker()
    cam = Camera(cam_t_queue)
    flash = FlashSync(flash_t_queue)
    trigger = TriggerHandler(trigger_t_queue)
    photo_sync = PhotoSync(GeneralSettings.capture_dir ,flash_t_queue,cam_t_queue )
    uav = mavlinkHandler(gps_data)
    imu = ImuHandler(imu_queue)

    broker.start()
    cam.start()
    flash.start()
    trigger.start()
    uav.start()
    photo_sync.start()
    imu.start()



    time.sleep(30)
    print(cam.is_alive())
    print(flash_t_queue.qsize())