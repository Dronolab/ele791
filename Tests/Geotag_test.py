from UavInteraction.UavMavlinkHandler import mavlinkHandler
import queue
import time
from Geotag.geotagPhoto import geotagPhoto

q = queue.Queue()
mav = mavlinkHandler(q)
p = geotagPhoto(None, q, None)
i = 0
while i < 2000:
    i += 1
    if i == 1000 :
        current = time.time()
    mav._process()

old = time.time()
x = p.getGpsDatafromQueue(current)
print(time.time()-old)
print(x)

