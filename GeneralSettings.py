
# Setting FAKEIO to true will disable the gpio check and gphoto2 camera class Used to developp without camera
FAKEIO = True

FLASHGPIOPIN = 298
TRIGGERGPIOPIN = 388

endpoint_sub = "tcp://127.0.0.1:5556"
endpoint_pub = "tcp://127.0.0.1:5555"

server_endpoint_sub = "tcp://*:5555"
server_endpoint_pub = "tcp://*:5556"

mavlink_endpoint = "udp:0.0.0.0:14555"