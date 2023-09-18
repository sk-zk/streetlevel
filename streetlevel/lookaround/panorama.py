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
    region_id: int
    """
    An additional key which appears in image URLs. I don't know what this is, 
    but I had to name it something, so ``region_id`` it is.
    """

    lat: float
    """
    Latitude of the panorama's location.
    """
    lon: float
    """
    Longitude of the panorama's location.
    """

    heading: float = None
    """
    Heading in radians, where 0° is north, 90° is west, 180° is south, 270° is east.
    
    This value is converted from a field in the API response which I don't really understand,
    and the resulting heading is occasionally inaccurate.
    
    I've yet to find a way to convert the pitch and roll.
    """

    coverage_type: CoverageType = None
    """
    Whether the coverage was taken by car or by backpack.
    """
    date: datetime = None
    """
    Capture date and time of the panorama (in UTC, not local time).
    """

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id}/{self.region_id} ({self.lat:.5f}, {self.lon:.5f})"
