import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import sys

import zmq
import GeneralSettings
from Utility.processAbstract import ProcessAbstract
from Utility.ZmqUtility.zmqSocket import createPubSocket, publishMsg

class Broker(ProcessAbstract):
    def __init__(self):
        ProcessAbstract.__init__(self)

    def softProcessStop(self):
        self._kill_pill.put("DIE")
        sock = createPubSocket()
        publishMsg(sock,"DIE")

    def _process(self):

        context_sub = zmq.Context()
        socket_sub = context_sub.socket(zmq.SUB)

        context_pub = zmq.Context()
        socket_pub = context_pub.socket(zmq.PUB)

        socket_sub.bind(GeneralSettings.server_endpoint_sub)
        socket_pub.bind(GeneralSettings.server_endpoint_pub)

        topicfilter = ""
        socket_sub.setsockopt_string(zmq.SUBSCRIBE, topicfilter)


        while self._kill_pill.empty():
            try:
                string = socket_sub.recv()
                # print(string)
                socket_pub.send(string)

            except KeyboardInterrupt:
                self.softProcessStop()
                socket_sub.close()
                socket_pub.close()
                context_sub.term()
                context_pub.term()
