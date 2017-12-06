import time
import queue
import sys, getopt
from Utility.DataStructure import  attitudeData

sys.path.append('.')
import RTIMU
import os.path
import time
import math


class imuHandler:
    SETTINGS_FILE = "RTIMULib"
    def __init__(self):
        self.dataQueue = queue.Queue()

    def startImuPoll(self):
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

        while True:
            if self.imu.IMURead():
                current_time = time.time()
                x, y, z = self.imu.getFusionData()
                data = attitudeData(x,y,z, current_time)
                self.dataQueue.not_empty
                print("%f %f %f" % (x,y,z))
                self.dataQueue.put(data)
                print(self.dataQueue.qsize())
            time.sleep(self.poll_interval * 1.0 / 1000.0)




