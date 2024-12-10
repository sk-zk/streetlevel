from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from .util import build_permalink


@dataclass
class JaPanorama:
    """
    Metadata of a Já 360 panorama.

    ID, latitude, longitude and heading are always present. The availability of other metadata depends on
    which function was called and what was returned by the API.
    """

    id: int
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    heading: float
    """Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west."""

    neighbors: List[JaPanorama] = None
    """A list of nearby panoramas."""
    date: CaptureDate = None
    """The month and year the panorama was captured."""

    pano_url: str = None
    """Part of the panorama tile URL."""
    blur_key: int = None
    """Part of the panorama tile URL."""

    street_names: List[StreetLabel] = None
    """
    Street name labels overlaid on this panorama, featuring the name of the street(s) the panorama
    is located on and the angles that the label appears at.
    
    The first entry is the name of the street the panorama is located on; subsequent
    entries label nearby streets at junctions. 
    
    Note that ``distance`` is ``None`` for the first entry.
    """
    address: Address = None
    """Nearest address to the panorama's location."""

    def permalink(self: JaPanorama, heading: float = 0.0, radians: bool = False) -> str:
        """
        Creates a permalink to a panorama at this location. Directly linking to a specific panorama
        by its ID does not appear to be possible.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Já.is Kort URL which will open the panorama at this location.
        """
        return build_permalink(self.lat, self.lon, heading=heading, radians=radians)

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"


@dataclass
class CaptureDate:
    """
    Capture date of a Já 360 panorama.
    """
    year: int
    """The year the panorama was taken."""
    month: int  #:
    """The month the panorama was taken."""

    def __str__(self):
        return f"{self.year}-{self.month:02d}"


@dataclass
class Address:
    """
    Nearest address to a Já 360 panorama.
    """
    street_name_and_house_number: str  #:
    postal_code: int  #:
    place: str  #:


@dataclass
class StreetLabel:
    """A label overlaid on the panorama in official road coverage displaying the name of a street."""
    name: str
    """The street name."""
    angles: List[float]
    """A list of different yaws that this street name appears at, in radians."""
    distance: Optional[int] = None
    """Distance from the camera, presumably in meters."""
