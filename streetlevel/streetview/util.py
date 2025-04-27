import math


def is_third_party_panoid(panoid: str) -> bool:
    """
    Returns whether a pano ID points to a third-party panorama rather than an official Google panorama.

    :param panoid: The pano ID.
    :return: Whether the pano ID points to a third-party panorama.
    """
    return panoid.startswith("CIHM0og") or len(panoid) > 22


def build_permalink(id: str = None, lat: float = None, lon: float = None,
                    heading: float = 0.0, pitch: float = 90.0, fov: float = 75.0,
                    radians: bool = False) -> str:
    """
    Creates a permalink to a panorama. All parameters are optional, but
    either a location, or a pano ID, or both must be passed.
    
    :param id: *(optional)* The pano ID.
    :param lat: *(optional)* Latitude of the panorama's location.
    :param lon: *(optional)* Longitude of the panorama's location.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 90°.
    :param fov: *(optional)* Initial FOV of the viewport. Defaults to 75°.
    :param radians: *(optional)* Whether viewport angles are in radians. Defaults to False.
    :return: A Google Maps URL which will open the given panorama.
    """
    # the reason I'm not creating a `map_action=pano` URL as described here
    # https://developers.google.com/maps/documentation/urls/get-started#street-view-action
    # is because third-party pano IDs do not appear to be work.
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
        fov = math.degrees(fov)
    return f"https://www.google.com/maps/@{lat},{lon},3a,{fov}y,{heading}h,{pitch}t" \
           f"/data=!3m4!1e1!3m2!1s{id}!2e{10 if is_third_party_panoid(id) else 2}"
