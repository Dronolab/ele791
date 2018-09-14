import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import time
import queue
from Utility.DataStructure import  attitudeData
from Utility.processAbstract import ProcessAbstract
sys.path.append('.')
import RTIMU
import os.path
import time
import math

import os


class ImuHandler(ProcessAbstract):
    SETTINGS_FILE = os.path.dirname(os.path.abspath(__file__))+"/RTIMULib"

    def __init__(self, imu_queue):
        self.dataQueue = imu_queue
        ProcessAbstract.__init__(self)

    def _process(self):

        print("Using settings file " + self.SETTINGS_FILE + ".ini")
        if not os.path.exists(self.SETTINGS_FILE + ".ini"):
            print("Settings file does not exist, will be created")

        s = RTIMU.Settings(self.SETTINGS_FILE)
        self.imu = RTIMU.RTIMU(s)

        if (not self.imu.IMUInit()):
            print("IMU Init Failed")
            sys.exit(1)
        else:
            print("IMU Init Succeeded")

        # initialising fusion parameters
        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)

        self.poll_interval = self.imu.IMUGetPollInterval()
        print("Recommended Poll Interval: %dmS\n" % self.poll_interval)

        while self._kill_pill.empty():
            try:
                if self.imu.IMURead():
                    current_time = time.time()
                    x, y, z = self.imu.getFusionData()
                    data = attitudeData(x,y,z, current_time)
                    # self.dataQueue.not_empty
                    # print("%f %f %f" % (math.degrees(x),math.degrees(y),math.degrees(z)))
                    self.dataQueue.put(data)
                    # print(self.dataQueue.qsize())

                time.sleep(self.poll_interval * 1.0 / 1000.0)
            except KeyboardInterrupt:
                self.softProcessStop()


