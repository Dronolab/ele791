import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


import time
import queue
import math
import os
from Utility.DataStructure import attitudeData, gpsData
from Utility.processAbstract import ProcessAbstract
from Utility.ZmqUtility.zmqSocket import createPubSocket, publishMsg
from Utility.ZmqUtility.MsgDefinition import PictureGeotagedFailed
import GeneralSettings
from Geotag import metadata
from GeneralSettings import logger

class GeotagPhoto(ProcessAbstract):
    def __init__(self, attitudeQueue, gpsQueue, uav_attitude_queue,  log_path=None):
        ProcessAbstract.__init__(self)
        self.attitudeQueue = attitudeQueue
        self.gpsQueue = gpsQueue
        self.uav_attitude_queue = uav_attitude_queue
        self.__log_path = log_path
        self.last_lat = None
        self.last_lon = None
        self.last_alt = None
        self.last_rel_alt = None
        self.last_hdg = None
        self.last_dyaw = None
        self.last_droll = None
        self.last_dpitch = None
        self.last_uav_pitch = None
        self.last_uav_roll = None
        self.last_uav_yaw = None

        for the_file in os.listdir(GeneralSettings.capture_dir):
            file_path = os.path.join(GeneralSettings.capture_dir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print("removing %s" %file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def geoTagPhoto(self, file_path):
        unix = self.getUnixFromPath(file_path)

        pass

    def _process(self):
        old_files = []
        bad_geotag_sock = createPubSocket()
        while self._kill_pill.empty():
            try:
                current_files = sorted(os.listdir(GeneralSettings.capture_dir))
                # print(current_files)
                for file in current_files:
                    if file not in old_files and not file.startswith("X_"):
                        data_flag = False

                        unix = self.getUnixFromPath(file)
                        # print("Unis is "+ str(unix))
                        if not unix:
                            logger.debug("File has no unix :" + str(file))
                            continue

                        logger.debug("Geotagging picture %s" %unix)
                        gps_data = self.getGpsDatafromQueue(unix)
                        imu_data = self.getAttitudeDatafromQueue(unix)
                        uav_data = self.getUavAttitudeDatafromQueue(unix)

                        lat = None
                        lon = None
                        alt = None
                        rel_alt = None
                        hdg = None
                        dyaw = None
                        droll = None
                        dpitch = None
                        uav_pitch = None
                        uav_roll = None
                        uav_yaw = None
                        gps_data_flag = True

                        if uav_data:
                            uav_pitch = uav_data.pitch
                            uav_roll = uav_data.roll
                            uav_yaw = uav_data.yaw
                            self.last_uav_pitch = uav_data.pitch
                            self.last_uav_roll = uav_data.roll
                            self.last_uav_yaw = uav_data.yaw
                            logger.debug("uav IMU data for file:%s pitch:%s, roll:%s, yaw:%s " %(file, uav_pitch, uav_roll, uav_yaw))

                        else:
                            logger.error("No uav imu data found in picture %s" %unix)

                        if gps_data:
                            alt = gps_data.alt
                            lat = gps_data.lat
                            lon = gps_data.lon
                            rel_alt =  gps_data.rel_alt
                            hdg = gps_data.hdg
                            self.last_lat = gps_data.lat
                            self.last_lon = gps_data.lon
                            self.last_alt = gps_data.alt
                            self.last_rel_alt = gps_data.rel_alt
                            self.last_hdg = gps_data.hdg

                            data_flag = True
                            logger.debug("Gps data for file %s is alt :%s lat:%s lon:%s" %(file,alt,lat,lon))
                        else:
                            logger.error("No gps data for picture %s" %unix)
                            gps_data_flag = False

                        if imu_data:
                            dpitch = math.degrees(imu_data.pitch)
                            droll = math.degrees(imu_data.roll)
                            dyaw = math.degrees(imu_data.yaw)
                            self.last_dyaw = dyaw
                            self.last_droll = droll
                            self.last_dpitch = dpitch
                            logger.debug("IMU data for file:%s dpitch:%s, droll:%s, dyaw:%s " %(file,dpitch,droll,dyaw))

                            data_flag = True
                        else:
                            logger.info("No imu data for picture %s" % unix)


                        if not (GeneralSettings.capture_dir.endswith("/")):
                            file_path = GeneralSettings.capture_dir + "/"+file

                        else:
                            file_path = GeneralSettings.capture_dir + file

                        metadata.xmp_write(file_path,rel_alt,alt,lat,lon,hdg,uav_pitch, uav_roll, uav_yaw, droll,dpitch,dyaw,-1,unix)

                        if gps_data:
                            print("exif write")
                            print(gps_data)
                            metadata.exif_write(file_path,lat,lon,hdg,alt)

                        prefix = "U_"
                        if data_flag:
                            prefix = "X_"

                        if not gps_data_flag:
                            msg = PictureGeotagedFailed()
                            publishMsg(bad_geotag_sock, msg.generateMsg())

                        if not (GeneralSettings.capture_dir.endswith("/")):
                            new_file_name = GeneralSettings.sync_dir + "/"+ prefix +file
                        else:
                            new_file_name = GeneralSettings.sync_dir  + prefix + file


                        os.rename(file_path,new_file_name)

                        old_files.append(new_file_name)


            except KeyboardInterrupt:

                self.softProcessStop()

            time.sleep(1)
    # return the before and after value from queue. Since having the exact timed data is impossible, we are getting
    #both the value befor and after the desired time and we can extrapolate the value based on the timelaps

    def valid_file(self,file_name):
        valid = True

        return valid


    def getUnixFromPath(self, file_path):

        unix = None
        # extracting file name from path
        file_name = os.path.basename(file_path)
        file_name = os.path.splitext(file_name)[0]
        try:
            unix = float(file_name)
        except:
            # not the best error handling .. will have to strip file name to unix in the future
            unix = None
            pass
        logger.info("the unix time is %s" %(str(unix)))

        return unix

    def getDataFromQueue(self,current_unix, data_queue):
        last_obj = None
        next_obj = None
        next_flag = 0
        if current_unix:
            while not data_queue.empty():
                obj = data_queue.get()
                if (current_unix > obj.unix):
                    last_obj = obj
                    next_flag = 1
                elif next_flag:
                    next_obj = obj
                    next_flag = 0
                    break
        return last_obj, next_obj

    def getAttitudeDatafromQueue(self,unix):
        last_att_obj , next_att_obj = self.getDataFromQueue(unix,self.attitudeQueue)
        att_obj = self.extrapolateAttitude(unix,last_att_obj,next_att_obj)
        return att_obj

    def getUavAttitudeDatafromQueue(self,unix):
        last_att_obj , next_att_obj = self.getDataFromQueue(unix,self.uav_attitude_queue)
        att_obj = self.extrapolateAttitude(unix,last_att_obj,next_att_obj)
        return att_obj

    def extrapolateAttitude(self, current_unix, last_att_obj, next_att_obj):
        att_obj = None
        if ((last_att_obj is not None) and (next_att_obj is not None)):
            pitch = self.linearExtrapolation(current_unix,
                                     last_att_obj.unix, last_att_obj.pitch,
                                     next_att_obj.unix, next_att_obj.pitch)
            roll = self.linearExtrapolation(current_unix,
                                     last_att_obj.unix, last_att_obj.roll,
                                     next_att_obj.unix, next_att_obj.roll)
            yaw = self.linearExtrapolation(current_unix,
                                     last_att_obj.unix, last_att_obj.yaw,
                                     next_att_obj.unix, next_att_obj.yaw)
            att_obj = attitudeData(pitch,roll,yaw,current_unix)

        elif(last_att_obj is not None):
            att_obj = attitudeData(last_att_obj.pitch,
                                   last_att_obj.roll,
                                   last_att_obj.yaw,
                                   current_unix)

        elif(next_att_obj is not None):
            att_obj = attitudeData(next_att_obj.pitch,
                                   next_att_obj.roll,
                                   next_att_obj.yaw,
                                   current_unix)

        return att_obj


    def getGpsDatafromQueue(self,unix):
        last_gps_obj , next_gps_obj = self.getDataFromQueue(unix,self.gpsQueue)
        gps_obj = self.extrapolateGps(unix,last_gps_obj,next_gps_obj)
        return gps_obj

    def extrapolateGps(self,current_unix, last_gps_obj, next_gps_obj):
        gps_obj = None

        if ((last_gps_obj is not None) and (next_gps_obj is not None)):
            lat = self.linearExtrapolation(current_unix,
                                             last_gps_obj.unix, last_gps_obj.lat,
                                             next_gps_obj.unix, next_gps_obj.lat)
            print("last Lat : %f Next lat %f extrapolated lat %f"%(last_gps_obj.lat, next_gps_obj.lat, lat))

            lon = self.linearExtrapolation(current_unix,
                                           last_gps_obj.unix, last_gps_obj.lon,
                                           next_gps_obj.unix, next_gps_obj.lon)
            alt = self.linearExtrapolation(current_unix,
                                           last_gps_obj.unix, last_gps_obj.alt,
                                           next_gps_obj.unix, next_gps_obj.alt)
            rel_alt = self.linearExtrapolation(current_unix,
                                           last_gps_obj.unix, last_gps_obj.rel_alt,
                                           next_gps_obj.unix, next_gps_obj.rel_alt)
            try:
                hdg = self.linearExtrapolation(current_unix,
                                                   last_gps_obj.unix, last_gps_obj.hdg,
                                                   next_gps_obj.unix, next_gps_obj.hdg)
            except:
                hdg = None
                pass
            gps_obj = gpsData(alt, lat, lon, rel_alt, current_unix, hdg)

        elif (last_gps_obj is not None):
            gps_obj = gpsData(last_gps_obj.alt,
                              last_gps_obj.lat,
                              last_gps_obj.lon,
                              last_gps_obj.rel_alt,
                              current_unix,
                              last_gps_obj.hdg)

        elif (next_gps_obj is not None):
            gps_obj = gpsData(next_gps_obj.alt,
                              next_gps_obj.lat,
                              next_gps_obj.lon,
                              next_gps_obj.rel_alt,
                              current_unix,
                              next_gps_obj.hdg)

        return gps_obj

    def linearExtrapolation(self,t, t0, y0, t1, y1):
        dy = (y1 - y0)
        dt = (t1 - t0)
        y = y0 + (t - t0) * (dy / dt)
        return y

