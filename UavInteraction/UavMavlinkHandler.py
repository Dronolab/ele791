import sys
sys.path.insert(0,'..')

import time
from multiprocessing import Process

from Utility.ZmqUtility.MsgDefinition import TakePicture
from pymavlink import mavutil
import math

from GeneralSettings import logger
from Utility.DataStructure import gpsData, attitudeData
from Utility.ZmqUtility import zmqSocket
from Utility.processAbstract import ProcessAbstract

class mavlinkHandler(ProcessAbstract):
    def __init__(self,gps_queue,attitude_queue):
        ProcessAbstract.__init__(self)
        logger.error("From mavlinkHander")
        # self.mavs = mavutil.mavlink_connection(GeneralSettings.mavlink_endpoint,baud=57600,source_system=1, input=True)
        self.mavserial = mavutil.MavlinkSerialPort("/dev/ttyUSB0", 57600)
        self.mavs = self.mavserial.mav
        self.gps_queue = gps_queue
        self.attitude_queue = attitude_queue

    def _process(self):
        self.zmq_pub_socket = zmqSocket.createPubSocket()

        while self._kill_pill.empty():
            try:
                msg = self.mavs.recv_match(blocking=True)
                # print(msg)
                msg_type = msg.get_type()
                # print(msg_type)

                if (msg_type == "HEARTBEAT"):
                    # print("HEARTBEAT")
                    pass

                if (msg_type == "CAMERA_TRIGGER"):
                    print("Camera_trigger from Mavlink")
                    self.cameraTriggerMsgHandler(msg)


                if (msg_type == "ATTITUDE"):
                    self.attitudeMsgHandler(msg)

                if(msg_type == 'COMMAND_ACK'):
                    print(msg)

                if (msg_type == "GLOBAL_POSITION_INT"):
                    self.globalPositionMsgHandler(msg)

                if msg_type =="SYSTEM_TIME":
                    self.systemTimeMsgHangler(msg)

                if msg_type == "GPS_RAW_INT":
                    self.gpsRawIntMsgHandler(msg)
            except KeyboardInterrupt:
                self.softProcessStop()

    def cameraTriggerMsgHandler(self,msg):
        seq = msg.seq
        trigger_action = TakePicture()
        trigger_action.setCaptureType(TakePicture.SINGLE)
        zmqSocket.publishMsg(self.zmq_pub_socket, trigger_action.generateMsg())

    def attitudeQuaternionMsgHandler(self, msg):
        timems_boot = msg.time_boot_ms
        q1 = msg.q1  # quaterion component 1 w
        q2 = msg.q2  # quaterion component 2 x
        q3 = msg.q3  # quaterion component 3 y
        q4 = msg.q4  # quaterion component 4 z

    def gpsRawIntMsgHandler(self, msg):
        time_usec = msg.time_usec / 1000000
        #print(msg.time_usec)
        fix_type = msg.fix_type
        lat = (msg.lat / 10000000)
        lon = (msg.lon / 10000000)
        alt = (msg.alt / 1000)
        hdop = msg.eph
        vdop = msg.epv
        satellites_visible = msg.satellites_visible

        #print("Unix %f, nbSatelites %i" % (time_usec, satellites_visible))
        #print("fix type %i" % fix_type)

    def attitudeMsgHandler(self, msg):
        pitch = math.degrees(msg.pitch)
        roll = math.degrees(msg.roll)
        yaw = math.degrees(msg.yaw)
        unix = time.time()
        att_data = attitudeData(pitch, roll, yaw, unix)
        self.attitude_queue.put(att_data)

    def globalPositionMsgHandler(self, msg):
        unix = time.time()
        lat = (msg.lat / 10000000)
        lon = (msg.lon / 10000000)
        alt = (msg.alt / 1000)
        rel_alt = (msg.relative_alt / 1000)
        hdg = (msg.hdg/100)
        #print(msg)
        gps_data = gpsData(alt, lat, lon, rel_alt, unix, hdg)
        self.gps_queue.put(gps_data)
        print(self.gps_queue.qsize())

    def systemTimeMsgHangler(self, msg):
        unix_time = msg.time_unix_usec
        ms_boot_time = msg.time_boot_ms
        # print("Unix time %lf, ms  boot %f" % (unix_time, ms_boot_time))
        # print(time.time())

