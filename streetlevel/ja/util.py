import math

from streetlevel import geo


def build_permalink(lat: float, lon: float, heading: float = 0.0, radians: bool = False) -> str:
    """
    Creates a permalink to the closest panorama to the given location.
    Directly linking to a specific panorama by its ID does not appear to be possible.

    :param lat: Latitude of the panorama's location.
    :param lon: Longitude of the panorama's location.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A Já.is Kort URL which will open the closest panorama to the given location.
    """
    if radians:
        heading = math.degrees(heading)
    # if the heading is exactly 0, ja.is will act as though it is not set
    # and choose a weird default value instead
    if heading == 0.0:
        heading = 0.0001
    x, y = geo.wgs84_to_isn93(lat, lon)
    return f"https://ja.is/kort/?nz=17&x={int(x)}&y={int(y)}&ja360=1&jh={heading}"
