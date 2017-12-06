class gpsData:
    def __init__(self, alt, lat, lon, rel_alt, unix, hdg = None):
        self.alt = alt
        self.lat = lat
        self.lon = lon
        self.rel_alt = rel_alt
        self.hdg = hdg
        self.unix = unix

class attitudeData:
    def __init__(self, pitch, roll, yaw, unix):
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.unix = unix
