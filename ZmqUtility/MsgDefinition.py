import json


#abstract class for message generation
class BaseMsg:
    TOPIC = ""
    def generateMsg(self):
        data = json.dumps(self.__dict__)
        msg = "%s %s" %(self.TOPIC, data)
        return msg

    #decode a json msg with from  topic
    def decodeMSG(self, msg):
        # print(msg)
        topic = msg.split()[0]
        msg = str(msg)
        msg = msg.replace(topic, "")
        messagedata = json.loads(msg)
        if topic == self.TOPIC:
            keys = self.__dict__.keys()
            for key in keys:
                if key is not "message_type":
                    setattr(self, key,messagedata.get(key, None))
        return messagedata.get("message_type", None)


class PictureGeotaged(BaseMsg):
    TOPIC = "picture_geotagged"
    def __init__(self):
        self.message_type = "picture_geotagged"
        self.file_path = None
        self.altitude = None

    def setFilePath(self, file_path):
        self.file_path = file_path

    def setAltitude(self,alt):
        self.altitude = alt

    def getFilePatg(self):
        return self.file_path

    def getAltitude(self):
        return self.altitude



class PictureTimeReferenced(BaseMsg):
    TOPIC = "picture_time_referenced"
    def __init__(self):
        self.message_type = "picture_time_referenced"
        self.time_referenced = None
        self.file_path = None

    def setTimeReference(self, time_ref):
        self.time_referenced = time_ref

    def getTimeReference(self):
        return self.time_referenced

    def setFilePath(self, path):
        self.file_path = path

    def getFilePath(self):
        return self.file_path


class PictureDownloaded(BaseMsg):
    TOPIC = "picture_downloaded"
    def __init__(self):
        self.message_type = "picture_downloaded"
        self.download_time = None
        self.file_path = None

    def setDownloadTime(self, time):
        self.download_time = time

    def getDownloadedTime(self):
        return self.download_time

    def setFilePath(self, path):
        self.file_path = path

    def getFilePath(self):
        return self.file_path


# picture taken topic is useed when we detect that the cameras has trigerreg
#normaly this topic is publish by the flash
# if the flash isnt working it can be emited by teh trigger but we gotta make sure the capture worked
class PictureTaken(BaseMsg):
    TOPIC = "picture_taken"
    def __init__(self):
        self.message_type = "picture_taken"
        self.capture_time = None

    def setCaptureTime(self, time):
        self.capture_time = time

    def getCaptureTime(self):
        return self.capture_time



class TakePicture(BaseMsg):
    TOPIC = "take_picture"
    def __init__(self):
        self.message_type = "take_picture"
        self.capture_type = None
        self.time_interval = None
        self.nb_capture_todo = None

    def setCaptureType(self, capt):
        self.capture_type = capt

    def getCaptureType(self):
        return self.capture_type

    def setTimeInterval(self, intv):
        self.time_interval = intv

    def getTimeInterval(self):
        return self.time_interval

    def setNbCaptureTodo(self,nb_capt):
        self.nb_capture_todo = nb_capt

    def getNbCaptureTodo(self):
        return self.nb_capture_todo

class TriggerAction(BaseMsg):
    TOPIC = "TRIGGER_ACTION"
    def __init__(self):
        self.message_type = "TRIGGER_ACTION"
        self.unix = None
        self.action = None

    def setUnixTime(self,unix):
        self.unix = unix
    def getUnixTime(self):
        return self.unix
    def setActionType(self,action):
        self.action = action
    def getActionType(self):
        return self.action

def MsgHandeler(msg):
    MsgList = [TakePicture(), PictureTaken(), PictureGeotaged(), PictureDownloaded(), PictureTimeReferenced(), TriggerAction()]
    topic = msg.split()[0]
    good_obj = None

    for obj in MsgList:
        if topic == obj.TOPIC:
            tmp = obj
            msg_type_tmp = tmp.decodeMSG(msg)

            # not implemented yet buf if topic has multiple msg type, we can only return one msg
            if tmp.message_type == msg_type_tmp:
                good_obj = tmp
            print(tmp.message_type)

    return good_obj
