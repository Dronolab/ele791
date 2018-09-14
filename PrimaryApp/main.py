import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import zmq
import time
import logging
from multiprocessing import Queue

import GeneralSettings
from GeneralSettings import logger
from Capture.CameraPTP import Camera
from Utility.ZmqUtility.zmqBroker import Broker
from Utility.ZmqUtility.MsgDefinition import PictureTaken, PictureDownloaded, PictureGeotagedFailed
from Capture.FlashSync import FlashSync
from Capture.TriggerHandler import TriggerHandler
from Capture.photoSync import PhotoSync
from Geotag.imuHandler import ImuHandler
from Geotag.geotagPhoto import GeotagPhoto
from Utility.ZmqUtility.zmqSocket import subReadMsg, createSubSocket
from UavInteraction.UavMavlinkHandler import mavlinkHandler



process = []

if __name__ == '__main__':

    flash_t_queue = Queue()
    cam_t_queue = Queue()
    trigger_t_queue = Queue()
    gps_data = Queue()
    imu_queue = Queue()
    uav_attitude_queue = Queue()

    logger.info("Starting main")

    cam = Camera(cam_t_queue)
    process.append(cam)

    logger.info("Camera init done")

    print("Camera init done")

    broker = Broker()
    process.append(broker)

    logger.info("Broker ini done")

    flash = FlashSync(flash_t_queue)
    process.append(flash)

    logger.info("Flashsync ini done")

    trigger = TriggerHandler(trigger_t_queue)
    process.append(trigger)

    logger.info("TriggerHandler ini done")

    photo_sync = PhotoSync(GeneralSettings.capture_dir ,flash_t_queue,cam_t_queue )
    process.append(photo_sync)

    logger.info("PhotoSync ini done")

    uav = mavlinkHandler(gps_data, uav_attitude_queue)
    process.append(uav)

    imu = ImuHandler(imu_queue)
    process.append(imu)
    logger.info("ImuHandler ini done")

    geotag = GeotagPhoto(imu_queue,gps_data, uav_attitude_queue)
    process.append(geotag)
    logger.info("GeotagPhoto ini done")

    for proc in process:
        proc.start()

    # broker.start()
    # cam.start()
    # flash.start()
    # trigger.start()
    # uav.start()
    # photo_sync.start()
    # imu.start()

    while True:
        try:
            time.sleep(0.5)
            #
            # for proc in process:
            #     if not proc.is_alive():
            #         pass
            #     # print(type(proc))
            #     # print("Need restart")
            # # print(type(proc))
            take_pic_sock = createSubSocket(PictureTaken.TOPIC)
            new_file_added_sock = createSubSocket(PictureDownloaded.TOPIC)
            new_file_added_sock.setsockopt(zmq.RCVTIMEO, 5000)
            geotag_fail_sock = createSubSocket(PictureGeotagedFailed.TOPIC)
            geotag_fail_sock.setsockopt(zmq.RCVTIMEO, 500)
            try:
               subReadMsg(take_pic_sock)
               base_time = time.time()
               subReadMsg(new_file_added_sock)
               print("It took us %f" %(time.time() - base_time))
            except zmq.error.Again :
                print("picture problem restarting!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                for proc in process:
                    print("Killing process")
                    proc.hardProcessStop()
                sys.exit()

            try:
                subReadMsg(geotag_fail_sock)

            except zmq.error.Again:
                pass
            else:
                print("picture geotagling problem restarting!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                for proc in process:
                    print("Killing process")
                    proc.hardProcessStop()
                sys.exit()

        except KeyboardInterrupt:
            time.sleep(2)
            for proc in process:
                print("Killing process")
                proc.hardProcessStop()
            sys.exit()