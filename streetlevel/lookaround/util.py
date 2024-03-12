import base64
import math

from streetlevel.lookaround.proto import MuninViewState_pb2


def build_permalink(lat: float, lon: float, heading: float = 0.0, pitch: float = 0.0,
                    radians: bool = False) -> str:
    """
    Creates a link which will open a panorama at the given location in Apple Maps.
    Linking to a specific panorama by its ID does not appear to be possible.

    On non-Apple devices, the link will redirect to Google Maps.

    :param lat: Latitude of the panorama's location.
    :param lon: Longitude of the panorama's location.
    :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
    :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
    :param radians: *(optional)* Whether angles are in radians. Defaults to False.
    :return: An Apple Maps URL which will open the closest panorama to the given location.
    """
    if radians:
        heading = math.degrees(heading)
        pitch = math.degrees(pitch)
    mvs = MuninViewState_pb2.MuninViewState()
    mvs.cameraFrame.latitude = lat
    mvs.cameraFrame.longitude = lon
    mvs.cameraFrame.yaw = heading
    mvs.cameraFrame.pitch = -pitch
    mvs_base64 = base64.b64encode(mvs.SerializeToString())
    return f"https://maps.apple.com/?ll={lat},{lon}&_mvs={mvs_base64.decode()}"
