import math


def build_permalink(id: str = None, lat: float = None, lon: float = None,
                    heading: float = 0.0, pitch: float = 0.0, map_zoom: float = 17.0,
                    radians: bool = True) -> str:
    """
    Creates a permalink to the given panorama. All parameters are optional, but
    either a location, or a pano ID, or both must be passed.

    :param id: *(optional)* The pano ID.
    :param lat: *(optional)* Latitude of the panorama's location.
    :param lon: *(optional)* Longitude of the panorama's location.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
    :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A Yandex Maps URL which will open the given panorama.
    """
    if id is None and (lat is None or lon is None):
        raise ValueError("You must pass a location, or pano ID, or both.")
    elif id is None:
        id = ""
    elif lat is None and lon is None:
        (lat, lon) = (0.0, 0.0)
    elif (lat is None and lon is not None) or (lat is not None and lon is None):
        raise ValueError("lat and lon must either both be set or both be null.")

    if radians:
        heading = math.degrees(heading)
        pitch = math.degrees(pitch)
    return f"https://yandex.com/maps/?" \
           f"&ll={lon}%2C{lat}" \
           f"&panorama%5Bdirection%5D={heading}%2C{pitch}" \
           f"&panorama%5Bfull%5D=true" \
           f"&panorama%5Bid%5D={id}" \
           f"&panorama%5Bpoint%5D={lon}%2C{lat}" \
           f"&z={map_zoom}"
