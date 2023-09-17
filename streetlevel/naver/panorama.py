from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List


class PanoramaType(IntEnum):
    """
    The panorama type. Most identifiers are taken directly from the source.
    """
    AIR = 1,  #:
    CAR = 3,  #:
    BICYCLE = 4,  #:
    INSIDE = 5,  #:
    INTERIOR = 7,  #:
    JIMMY_JIB = 8,  #:
    INDOOR = 10,  #:
    TREKKER = 13,  #:
    UNDERWATER = 12,  #:
    INDOOR_3D = 100,  #:


@dataclass
class NaverPanorama:
    """
    Metadata of a Naver Street View panorama.

    ID, latitude and longitude are always present. The availability of other metadata depends on which function
    was called and what was returned by the API.
    """

    id: str
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    heading: float = None
    """Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west."""

    max_zoom: int = None
    """Highest zoom level available for this panorama."""

    neighbors: Neighbors = None
    """A list of nearby panoramas."""
    historical: List[NaverPanorama] = None
    """A list of panoramas with a different date at the same location. 
    Only available if the panorama was retrieved by ``find_panorama_by_id``."""
    timeline_id: str = None
    """The pano ID that must be given to the API to retrieve the full list of historical panoramas, which is also
    the ID of the most recent panorama at this location. If an earlier ID is used, only panoramas up to that date
    are returned."""

    date: datetime = None
    """Capture date and time of the panorama in UTC."""
    is_latest: bool = None
    """Whether this is the most recent panorama at its location."""

    description: str = None
    """The description field, which typically contains the neighborhood and city."""
    title: str = None
    """The title field, which typically contains the street name."""

    panorama_type: PanoramaType = None
    """The panorama type. Most identifiers are taken directly from the source."""
    overlay: Overlay = None
    """
    Curiously, Naver masks their car twice: once with an image of a car baked into the panorama, and additionally
    with an image of the road beneath it (like Google and Apple), which is served as a separate file and overlaid
    on the panorama in the client. This is the URL to that secondary overlay.
    
    (Only available for car footage.)
    """

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"


@dataclass
class Overlay:
    """URLs to the images from which the overlay hiding the mapping car is created."""

    source: str
    """URL to the texture."""
    mask: str
    """URL to the mask."""


@dataclass
class Neighbors:
    """Nearby panoramas."""

    street: List[NaverPanorama]
    """Nearby panoramas taken at street level."""
    other: List[NaverPanorama]
    """Nearby aerial or underwater panoramas."""
