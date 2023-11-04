from __future__ import annotations
from dataclasses import dataclass
from typing import List
import math

from .. import geo


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
    """ """

    neighbors: List[JaPanorama] = None
    """A list of nearby panoramas."""
    date: CaptureDate = None
    """The month and year the panorama was captured."""

    pano_url: str = None
    """Part of the panorama tile URL."""
    blur_key: int = None
    """Part of the panorama tile URL."""

    street_name: str = None
    """Name of the street."""
    address: Address = None
    """Nearest address to the capture location."""

    def permalink(self: JaPanorama, heading: float = 0.0, radians: bool = False) -> str:
        """
        Creates a permalink to a panorama at this location. Directly linking to a specific panorama
        by its ID does not appear to be possible.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Já.is Kort URL.
        """
        if radians:
            heading = math.degrees(heading)
        # if the heading is exactly 0, ja.is will act as though it is not set
        # and choose a weird default value instead
        if heading == 0.0:
            heading = 0.0001
        x, y = geo.wgs84_to_isn93(self.lat, self.lon)
        x = int(x)
        y = int(y)
        return f"https://ja.is/kort/?nz=17&x={x}&y={y}&ja360=1&jh={heading}"


@dataclass
class CaptureDate:
    """
    Capture date of a Já 360 panorama.
    """
    year: int  #:
    month: int  #:

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
