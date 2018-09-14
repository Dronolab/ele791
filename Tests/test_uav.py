import sys
sys.path.insert(0,'..')

from UavInteraction.UavMavlinkHandler import mavlinkHandler
import queue
import time
from Geotag.geotagPhoto import geotagPhoto


q = queue.Queue()
mav = mavlinkHandler(q)

mav.start()

time.sleep(30)