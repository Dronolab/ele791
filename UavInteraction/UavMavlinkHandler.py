import time
from multiprocessing import Process

from Utility.ZmqUtility.MsgDefinition import TakePicture
from pymavlink import mavutil

import GeneralSettings
from Utility.DataStructure import gpsData
from Utility.ZmqUtility import zmqSocket


class mavlinkHandler:
    def __init__(self,gps_queue):
        self.mavs = mavutil.mavlink_connection(GeneralSettings.mavlink_endpoint, input=True)
        self.zmq_pub_socket = zmqSocket.createPubSocket()
        self.gps_queue = gps_queue

    def createNewProcess(self):
        self._proc = Process(target=self._process)
        self._proc.daemon = True

    def start(self):
        if not self._proc == None:
            self._proc.start()

    def hardProcessStop(self):
        self._proc.terminate()

    def softProcessStop(self):
        self._kill = True
        self._proc.join()

    def _process(self):
        msg = self.mavs.recv_match(blocking=True)
        msg_type = msg.get_type()
        if (msg_type == "HEARTBEAT"):
            pass
        if (msg_type == "CAMERA_TRIGGER"):
            self.cameraTriggerMsgHandler(msg)
            trigger_action = TakePicture()
            trigger_action.setCaptureType(TakePicture.SINGLE)
            zmqSocket.publishMsg(self.zmq_pub_socket, trigger_action.generateMsg())

        # if (msg_type == "ATTITUDE"):
        #     self.attitudeMsgHandler(msg)

        if (msg_type == "GLOBAL_POSITION_INT"):
            self.globalPositionMsgHandler(msg)

        if msg_type =="SYSTEM_TIME":
            self.systemTimeMsgHangler(msg)

        if msg_type == "GPS_RAW_INT":
            self.gpsRawIntMsgHandler(msg)

    def cameraTriggerMsgHandler(self,msg):
        seq = msg.seq

    def attitudeQuaternionMsgHandler(self, msg):
        timems_boot = msg.time_boot_ms
        q1 = msg.q1  # quaterion component 1 w
        q2 = msg.q2  # quaterion component 2 x
        q3 = msg.q3  # quaterion component 3 y
        q4 = msg.q4  # quaterion component 4 z

    def gpsRawIntMsgHandler(self, msg):
        time_usec = msg.time_usec / 1000000
        print(msg.time_usec)
        fix_type = msg.fix_type
        lat = (msg.lat / 10000000)
        lon = (msg.lon / 10000000)
        alt = (msg.alt / 1000)
        hdop = msg.eph
        vdop = msg.epv
        satellites_visible = msg.satellites_visible

        print("Unix %f, nbSatelites %i" % (time_usec, satellites_visible))
        print("fix type %i" % fix_type)

    def attitudeMsgHandler(self, msg):
        pitch = msg.pitch
        roll = msg.roll
        yaw = msg.yaw
        print("Pitch: %f, Roll, %f, Yaw %f" % (pitch, roll, yaw))

    def globalPositionMsgHandler(self, msg):
        unix = time.time()
        lat = (msg.lat / 10000000)
        lon = (msg.lon / 10000000)
        alt = (msg.alt / 1000)
        rel_alt = (msg.relative_alt / 1000)
        hdg = msg.hdg
        gps_data = gpsData(alt, lat, lon, rel_alt, unix, hdg)
        self.gps_queue.put(gps_data)


    def systemTimeMsgHangler(self, msg):
        unix_time = msg.time_unix_usec
        ms_boot_time = msg.time_boot_ms
        print("Unix time %lf, ms  boot %f" % (unix_time, ms_boot_time))

