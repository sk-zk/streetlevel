import math


def build_permalink(id: str, heading: float = 0.0, pitch: float = 0.0,
                    radians: bool = True) -> str:
    """
    Creates a permalink to the given panorama.

    :param id: The pano ID.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A Baidu Maps URL which will open the given panorama.
    """
    if radians:
        heading = math.degrees(heading)
        pitch = math.degrees(pitch)
    return f"https://map.baidu.com/#panoid={id}" \
           f"&panotype=street&heading={heading}&pitch={pitch}&tn=B_NORMAL_MAP"
