import zmq
import GeneralSettings
import json

def createPubSocket():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(GeneralSettings.endpoint_pub)
    return socket

def createSubSocket(topic_filter):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(GeneralSettings.endpoint_sub)
    socket.setsockopt_string(zmq.SUBSCRIBE, topic_filter)
    return socket

def publishMsg(socket, topic, msg):
    print(msg)
    socket.send_string("%s %s" % (topic, msg))


def subReadMsg(socket):
    string = socket.recv()
    return string


def createMSG(keys, values):
    data = {}
    if len(keys) == len(values):
        for i in range (len(keys)):
            data[keys[i]] = values[i]

    if not data == {}:
        return json.dumps(data)
    else:
        return None

def createTakePictureMsg(capt_type, time_int, nb_capt ):
    keys = ["message_type", "capture_type", "time_interval", "nb_capture"]
    values = ["take_picture", capt_type, time_int, nb_capt]

    if len(keys) == len(values):
       return createMSG(keys,values)
    else :
        return None


def createPictureTakenMsg(capture_time):
    keys = ["message_type", "capture_time"]
    values = ["picture_taken", capture_time]

    if len(keys) == len(values):
       return createMSG(keys,values)
    else :
        return None

