from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
    batch_id: int
    """
    An additional parameter required for requesting the imagery, which I presume is an upload batch ID
    of some sort: every time Apple publishes a bunch of panoramas, they are assigned an ID as a kind of
    revision number.
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

    has_blurs: bool = None
    """Whether something in this panorama, typically a building, has been blurred."""

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id}/{self.batch_id} ({self.lat:.5f}, {self.lon:.5f})"
