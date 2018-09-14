import logging

# Setting FAKEIO to true will disable the gpio check and gphoto2 camera class Used to developp without camera
FAKEIO = False

FLASHGPIOPIN = 298
TRIGGERGPIOPIN = 388
CAMALIMGPIO = 480

#orbitty 298 == P4-8
#orbitty 298 == P4-7

endpoint_sub = "tcp://127.0.0.1:5556"
endpoint_pub = "tcp://127.0.0.1:5555"

server_endpoint_sub = "tcp://*:5555"
server_endpoint_pub = "tcp://*:5556"

# mavlink_endpoint = "udp:0.0.0.0:14555"
mavlink_endpoint ="/dev/ttyUSB0"


GimbalFlag = 1

capture_dir = "/home/nvidia/Capture/"
sync_dir = "/home/nvidia/Sync/"

log_file = "/home/nvidia/logfile.log"


logger = logging.getLogger('DronoObc_main')
hdlr = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)