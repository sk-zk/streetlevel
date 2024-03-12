import math
from dataclasses import dataclass
from datetime import datetime

from .util import build_permalink


@dataclass
class StreetsidePanorama:
    """
    Metadata of a Streetside panorama.
    """

    id: int
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""
    date: datetime
    """Capture date and time of the panorama."""
    next: int = None
    """ID of the next image in the sequence."""
    previous: int = None
    """ID of the previous image in the sequence."""
    elevation: int = None
    """Elevation at the capture location in meters."""
    heading: float = None
    """Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west."""
    pitch: float = None
    """Pitch offset for upright correction of the panorama, in radians."""
    roll: float = None
    """Roll offset for upright correction of the panorama, in radians."""
    max_zoom: int = None
    """
    Highest zoom level available; 
    4 for the original Microsoft panoramas, 3 for the TomTom-provided ones.
    """

    def permalink(self, heading: float = 0.0, pitch: float = 0.0,
                  map_zoom: float = 17.0, radians: bool = False) -> str:
        """
        Creates a permalink to the closest panorama to the given location.
        Directly linking to a specific panorama by its ID does not appear to be possible.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Bing Maps URL which will open the closest panorama to the given location.
        """
        return build_permalink(self.lat, self.lon, heading=heading, pitch=pitch,
                               map_zoom=map_zoom, radians=radians)

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"
