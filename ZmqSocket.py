import zmq
import GeneralSettings


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

