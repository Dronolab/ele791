import time
import queue
import os
from Utility.DataStructure import attitudeData, gpsData

class geotagPhoto:
    def __init__(self, attitudeQueue, gpsQueue, log_path=None):
        self.attitudeQueue = attitudeQueue
        self.gpsQueue = gpsQueue
        self.__log_path = log_path

    def geoTagPhoto(self, file_path):
        unix = self.getUnixFromPath(file_path)

        pass

    # return the before and after value from queue. Since having the exact timed data is impossible, we are getting
    #both the value befor and after the desired time and we can extrapolate the value based on the timelaps

    # def findValuesFromQueue(self, unix, dataQueue):
    #     beforeData = None
    #     afterData = None
    #
    #     while True:
    #         #will have to introduce a time limit for the get
    #         afterData = dataQueue.get()
    #
    #         if afterData.unix < unix:
    #             # will have to do a log before scraping the data
    #             beforeData = afterData
    #
    #         else:
    #             # will have to introduce a methode te break if the data isnt there
    #             break
    #
    #     return beforeData, afterData

    def getUnixFromPath(self, file_path):

        unix = None
        # extracting file name from path
        file_name = os.path.basename(file_path)
        file_name = os.path.splitext(file_name)[0]

        try:
            unix = float(file_name)
        except:
            # not the best error handling .. will have to strip file name to unix in the future
            pass
        print(unix)

        return unix

    def getDataFromQueue(self,current_unix, data_queue):
        last_obj = None
        next_obj = None
        next_flag = 0
        while not data_queue.empty():
            obj = data_queue.get()
            if (current_unix > obj.unix):
                last_obj = obj
                next_flag = 1
            elif next_flag:
                next_obj = obj
                next_flag = 0
        return last_obj, next_obj

    def getAttitudeDatafromQueue(self,unix):
        last_att_obj , next_att_obj = self.getDataFromQueue(unix,self.attitudeQueue)
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



# path_name = 'D:\ele791\\01-Capture\Photo\\1510268749.6838677.jpg'
# geotagPhoto.getUnixFromPath(geotagPhoto(1,1,1),path_name)