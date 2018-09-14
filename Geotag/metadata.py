import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import pyexiv2
import struct
import datetime
import fractions
import math
import GeneralSettings

pyexiv2.xmp.register_namespace('http://dronolab.com/', 'dronolab')


def to_dddmm_mmmmk(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    value = abs(value)
    a, b = divmod(value, 1)
    a = int(a)
    b *= 60
    b = "{:.4f}".format(b)
    return str(a) + ',' + str(b) + loc_value


def to_deg(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    _min = int(t1)
    sec = round((t1 - _min) * 60, 5)
    return deg, _min, sec, loc_value


def xmp_write(file_path, alt_agl, alt_msl, lat, lng, hdg,
              drll, dpch, dyaw,
              uav_pitch,uav_roll, uav_yaw,
              imgw,
              ts):


    metadata = pyexiv2.ImageMetadata(file_path)
    metadata.read()

    if alt_agl:
        metadata['Xmp.dronolab.RelativeAltitude'] = str(alt_agl)

    if alt_msl:
        metadata['Xmp.dronolab.AbsoluteAltitude'] = str(alt_msl)

    if lng:
        metadata['Xmp.dronolab.GPSLongitude'] = str(lng)

    if lat:
        metadata['Xmp.dronolab.GPSLatitude'] = str(lat)

    if lng and lat:
        metadata['Xmp.dronolab.GPSFlag'] = str('1')
    else:
        metadata['Xmp.dronolab.GPSFlag'] = str('0')

    if hdg:
        metadata['Xmp.dronolab.GPSBearing'] = str(hdg)
        metadata['Xmp.dronolab.GPSBearingRef'] = 'MAGNETIC'

    if drll:
        metadata['Xmp.dronolab.GimbalRollDegree'] = str(drll)

    if dpch:
        metadata['Xmp.dronolab.GimbalPitchDegree'] = str(dpch)

    if dyaw:
        metadata['Xmp.dronolab.GimbalYawDegree'] = str(dyaw)

    if GeneralSettings.GimbalFlag:
        metadata['Xmp.dronolab.GimbalFlag'] = str('1')
    else:
        metadata['Xmp.dronolab.GimbalFlag'] = str('0')

    if uav_pitch:
        metadata['Xmp.dronolab.UAVPitchDegree'] = str(uav_pitch)
    if uav_roll:
        metadata['Xmp.dronolab.UAVRollDegree'] = str(uav_roll)
    if uav_yaw:
        metadata['Xmp.dronolab.UAVYawDegree'] = str(uav_yaw)
    if imgw:
        metadata['Xmp.dronolab.ImageWeight'] = str(imgw)

    print(ts)
    if ts:
        metadata['Xmp.dronolab.TimeStamp'] = to_xmp_format_timestamp(int(ts))

    metadata.write()


def to_xmp_format_timestamp(dt):
    return datetime.datetime.utcfromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")


class Fraction(fractions.Fraction):

    def __new__(cls, value, ignore=None):
        """Should be compatible with Python 2.6, though untested."""
        return fractions.Fraction.from_float(value).limit_denominator(99999)

def dms_to_decimal(degrees, minutes, seconds, sign=' '):

    return (-1 if sign[0] in 'SWsw' else 1) * (
        float(degrees)        +
        float(minutes) / 60   +
        float(seconds) / 3600
    )


def decimal_to_dms(decimal):

    remainder, degrees = math.modf(abs(decimal))
    remainder, minutes = math.modf(remainder * 60)
    return [Fraction(n) for n in (degrees, minutes, remainder * 60)]

def exif_write(file_path, lat, lng, hdg, alt):


    exiv_image = pyexiv2.ImageMetadata(file_path)
    exiv_image.read()
    exif_keys = exiv_image.exif_keys

    if alt < 0:
        rel_byte = '1'
    else:
        rel_byte = '0'

    exiv_alt = Fraction(alt)
    exiv_hdg = Fraction(hdg)


    exiv_image["Exif.GPSInfo.GPSLatitude"] = decimal_to_dms(lat)
    exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = 'N' if lat >= 0 else 'S'
    exiv_image["Exif.GPSInfo.GPSLongitude"] = decimal_to_dms(lng)
    exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = 'E' if lng >= 0 else 'W'
    exiv_image["Exif.Image.GPSTag"] = 654
    exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    exiv_image["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
    exiv_image["Exif.GPSInfo.GPSDestBearing"] = exiv_hdg
    exiv_image["Exif.GPSInfo.GPSDestBearingRef"] = 'M'
    exiv_image["Exif.GPSInfo.GPSAltitude"] = exiv_alt
    exiv_image["Exif.GPSInfo.GPSAltitudeRef"] = rel_byte


    exiv_image.write()
