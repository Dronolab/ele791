import ZmqSocket

socket = ZmqSocket.createSubSocket("")

while 1 :
    msg = ZmqSocket.subReadMsg(socket)
    topic, messagedata = msg.split()
    print(msg)
