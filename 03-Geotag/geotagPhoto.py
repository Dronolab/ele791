import time
import queue
import os

class geotagPhoto:
    def __init__(self, attitudeQueue, gpsQueue, log_path):
        self.attitudeQueue = attitudeQueue
        self.gpsQueue = gpsQueue
        self.__log_path = log_path

    def geoTagPhoto(self, file_path):
        unix = self.getUnixFromPath(file_path)

        pass

    # return the before and after value from queue. Since having the exact timed data is impossible, we are getting
    #both the value befor and after the desired time and we can extrapolate the value based on the timelaps

    def findValuesFromQueue(self, unix, dataQueue):
        beforeData = None
        afterData = None

        while True:
            #will have to introduce a time limit for the get
            afterData = dataQueue.get()

            if afterData.unix < unix:
                # will have to do a log before scraping the data
                beforeData = afterData

            else:
                # will have to introduce a methode te break if the data isnt there
                break

        return beforeData, afterData

    def extrValues(self, unix, beforeData, afterData):
        pass

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



path_name = 'D:\ele791\\01-Capture\Photo\\1510268749.6838677.jpg'
geotagPhoto.getUnixFromPath(geotagPhoto(1,1,1),path_name)