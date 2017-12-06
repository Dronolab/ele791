import exifread
import time
import PIL.Image

path_name = 'D:\ele791\\01-Capture\Photo\\1510268689.4403527.jpg'
# Open image file for reading (binary mode)
base_time = time.time()
f = open(path_name, 'rb')

# Return Exif tags
tags = exifread.process_file(f)

print(time.time()-base_time)

path_name = 'D:\ele791\\01-Capture\Photo\\1510268749.6838677.jpg'
# Open image file for reading (binary mode)
base_time = time.time()
f = open(path_name, 'rb')

# Return Exif tags
tags = exifread.process_file(f)

print(time.time()-base_time)

# for tag in tags:
#     print(tag)
#
# base_time = time.time()
# img = PIL.Image.open(path_name)
# exif_data = img._getexif()
#
# print(time.time()-base_time)
# for tag in exif_data:
#     print(tag)