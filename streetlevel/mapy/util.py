import math


def build_permalink(id: int = None, lat: float = None, lon: float = None,
                    heading: float = 0.0, pitch: float = 0.0, fov: float = 72.0,
                    map_zoom: float = 17.0, radians: bool = False) -> str:
    """
    Creates a permalink to the given panorama. All parameters are optional, but
    either a location, or a pano ID, or both must be passed.

    :param id: *(optional)* The pano ID.
    :param lat: *(optional)* Latitude of the panorama's location.
    :param lon: *(optional)* Longitude of the panorama's location.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
    :param fov: *(optional)* Initial FOV of the viewport. Defaults to 72°.
    :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: A Mapy.cz URL which will open the given panorama.
    """
    newest = 0
    if id is None and (lat is None or lon is None):
        raise ValueError("You must pass a location, or pano ID, or both.")
    elif id is None:
        id = 0
        newest = 1
    elif lat is None and lon is None:
        (lat, lon) = (0.0, 0.0)
    elif (lat is None and lon is not None) or (lat is not None and lon is None):
        raise ValueError("lat and lon must either both be set or both be null.")

    if not radians:
        heading = math.radians(heading)
        pitch = math.radians(pitch)
        fov = math.radians(fov)
    return f"https://en.mapy.cz/zakladni?pano=1&pid={id}" \
           f"&newest={newest}&yaw={heading}&fov={fov}&pitch={pitch}&x={lon}&y={lat}" \
           f"&z={map_zoom}&ovl=8"
