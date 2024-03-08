import math


def build_permalink(id: str, heading: float = 0.0, pitch: float = 10.0,
                    fov: float = 80.0, map_zoom: float = 17.0, radians: bool = False) -> str:
    """
    Creates a permalink to the given panorama.

    :param id: The pano ID.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 10°.
    :param fov: *(optional)* Initial FOV of the viewport. Defaults to 80°.
    :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A Naver Map URL which will open the given panorama.
    """
    if radians:
        heading = math.degrees(heading)
        pitch = math.degrees(pitch)
        fov = math.degrees(fov)
    return f"https://map.naver.com/p?c={map_zoom},0,0,0,adh&p={id},{heading},{pitch},{fov},Float"
