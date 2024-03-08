import math

import numpy as np


def build_permalink(lat: float, lon: float, heading: float = 0.0, pitch: float = 0.0,
                    map_zoom: float = 17.0, radians: bool = False) -> str:
    """
    Creates a permalink to the closest panorama to the given location.
    Directly linking to a specific panorama by its ID does not appear to be possible.

    :param lat: Latitude of the panorama's location.
    :param lon: Longitude of the panorama's location.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
    :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A Bing Maps URL which will open the closest panorama to the given location.
    """
    if radians:
        heading = math.degrees(heading)
        pitch = math.degrees(pitch)
    return f"https://www.bing.com/maps?cp={lat}%7E{lon}&lvl={map_zoom}&v=2&sV=1" \
           f"&pi={pitch}&style=x&dir={heading}"


def to_base4(n: int) -> str:
    """
    Converts an integer to a base 4 string.

    :param n: The integer.
    :return: The base 4 representation of the integer.
    """
    return np.base_repr(n, 4)


def from_base4(n: str) -> int:
    """
    Converts a string containing a base 4 number to integer.

    :param n: The string containing a base 4 number.
    :return: The integer represented by the string.
    """
    return int(n, 4)
