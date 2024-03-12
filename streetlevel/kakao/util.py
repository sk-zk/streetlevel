import math


def build_permalink(id: int = None, wcongx: float = None, wcongy: float = None,
                    heading: float = 0.0, pitch: float = 0.0, radians: bool = False) -> str:
    """
    Creates a permalink to a panorama. All parameters are optional, but
    either a location, or a pano ID, or both must be passed.

    When linking by ID, the link will only work as expected for the most recent coverage
    at a location -- it does not appear to be possible to directly link to older panoramas.

    :param id: *(optional)* The pano ID.
    :param wcongx: *(optional)* X coordinate of the panorama's location in the WCongnamul coordinate system.
    :param wcongy: *(optional)* Y coordinate of the panorama's location in the WCongnamul coordinate system.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A KakaoMap URL which will open the given panorama.
    """
    if id is None and (wcongx is None or wcongy is None):
        raise ValueError("You must pass a location, or pano ID, or both.")
    elif id is None:
        id = 0
    elif wcongx is None and wcongy is None:
        (wcongx, wcongy) = (0.0, 0.0)
    elif (wcongx is None and wcongy is not None) or (wcongx is not None and wcongy is None):
        raise ValueError("wcongx and wcongx must either both be set or both be null.")

    if radians:
        heading = math.degrees(heading)
        pitch = math.degrees(pitch)
    url = f"https://map.kakao.com/?map_type=TYPE_MAP&map_attribute=ROADVIEW&panoid={id}" \
          f"&urlX={wcongx}&urlY={wcongy}&pan={heading}&tilt={pitch}&zoom=0&urlLevel=3"
    return url
