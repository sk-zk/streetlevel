from __future__ import annotations
from dataclasses import dataclass
from typing import List


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
