from PIL import Image
import numpy as np


def resize_by_altitude(image, altitude, ppm=32):
    """ Resize image based on altitude and expected ground resolution.

    Use Angle of view calculations to resize an image based on an altitude and
    a ground resolution.

    Arguments:
        image: Pillow image instance.
        altitude: distance to the ground.
        ppm: expected ground resolution in pixels per meter (ppm)

    Returns:
        resized Pillow image.

    """
    assert isinstance(image, Image.Image), "'image' is not a Pillow Image"
    focal = 16.0        # mm
    sensor_h = 15.6     # mm
    sensor_h_px = 3376

    actual_ppm = sensor_h_px / ((sensor_h / focal) * altitude)
    rsz = ppm / actual_ppm

    size = image.size
    new_size = tuple(int(s * rsz) for s in size)

    return image.resize(new_size), new_size


def to_nptiles(image, tile_shape=(32, 32), overlap=0.5):
    """ Convert Image to a list of numpy tiles of size tile_shape.

    Arguments:
        image: Pillow Image to convert.
        tile_shape: shape of a single tile.
        overlap: overlapping ratio of tiles. if 0.5, the second half of tile n
            is the first half of tile n+1.

    Returns:
        list of nparray tiles.

    """
    assert isinstance(image, Image.Image), "'image' is not a Pillow Image"
    assert 0 <= overlap < 1

    image_width, image_height = image.size
    box_width, box_height = tile_shape

    count = int(image_width / (box_width * (1 - overlap)) *
                image_height / (box_height * (1 - overlap)))

    i = 0
    tiles = np.zeros(shape=(count, box_width, box_height, 3))
    boxes = []
    (left, upper, right, lower) = (0, 0, box_width, box_height)

    while lower < image_height + (1 - overlap) * box_height / 2:
        while right < image_width + (1 - overlap) * box_width / 2:
            t = image.crop((left, upper, right, lower))
            tiles[i, :, :, :] = np.asarray(t)
            boxes.append((left, upper, right, lower))
            i += 1
            (left, upper, right, lower) = (left + (1 - overlap) * box_width,
                                           upper,
                                           right + (1 - overlap) * box_width,
                                           lower)

        (left, upper, right, lower) = (0,
                                       upper + (1 - overlap) * box_height,
                                       box_width,
                                       lower + (1 - overlap) * box_height)

    return tiles, boxes
