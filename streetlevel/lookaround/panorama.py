from __future__ import annotations

import base64
import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from streetlevel.lookaround.proto import MuninViewState_pb2


class CoverageType(Enum):
    """
    Coverage type of a Look Around panorama.
    """
    CAR = 2
    """
    The panorama was taken by a car.
    """
    BACKPACK = 3
    """
    The panorama was taken by a backpack.
    """


@dataclass
class LookaroundPanorama:
    """
    Metadata of a Look Around panorama.
    """

    id: int
    """The pano ID."""
    build_id: int
    """
    An additional parameter required for requesting the imagery. Every time Apple publishes or updates 
    a bunch of panoramas, they are assigned a build ID to act as a revision number.
    """

    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    heading: float = None
    """
    Heading in radians, where 0° is north, 90° is west, 180° is south, 270° is east.
    
    This value is converted from a field in the API response which I don't really understand,
    and the resulting heading is occasionally inaccurate.
    
    I've yet to find a way to convert the pitch and roll.
    """

    coverage_type: CoverageType = None
    """Whether the coverage was taken by car or by backpack."""
    date: datetime = None
    """Capture date and time of the panorama (in UTC, not local time)."""

    elevation: float = None
    """Elevation at the capture location in meters."""

    has_blurs: bool = None
    """Whether something in this panorama, typically a building, has been blurred."""

    def permalink(self: LookaroundPanorama, heading: float = 0.0, pitch: float = 0.0, radians: bool = False) -> str:
        """
        Creates a link which will open a panorama at this location in Apple Maps. Linking to a specific panorama
        by its ID does not appear to be possible.

        On non-Apple devices, the link will redirect to Google Maps.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: An Apple Maps URL.
        """
        if radians:
            heading = math.degrees(heading)
            pitch = math.degrees(pitch)
        mvs = MuninViewState_pb2.MuninViewState()
        mvs.viewState.latitude = self.lat
        mvs.viewState.longitude = self.lon
        mvs.viewState.yaw = heading
        mvs.viewState.pitch = -pitch
        mvs_base64 = base64.b64encode(mvs.SerializeToString())
        return f"https://maps.apple.com/?ll={self.lat},{self.lon}&_mvs={mvs_base64.decode()}"

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id}/{self.build_id} ({self.lat:.5f}, {self.lon:.5f})"
