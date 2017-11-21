from ZmqUtility import zmqSocket

socket = zmqSocket.createSubSocket("")

while 1 :
    msg = zmqSocket.subReadMsg(socket)
    topic, messagedata = msg.split()
    print(msg)
