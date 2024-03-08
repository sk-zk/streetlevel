from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from streetlevel.dataclasses import Size, Link
from .util import build_permalink


@dataclass
class YandexPanorama:
    """
    Metadata of a Yandex panorama.

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
    """Heading in radians, where 0° is south, 90° is west, 180° is north and 270° is east."""

    image_id: str = None
    """Part of the panorama tile URL."""
    tile_size: Size = None
    """Yandex panoramas are broken up into a grid of tiles. This returns the size of one tile."""
    image_sizes: List[Size] = None
    """
    The image sizes in which this panorama can be downloaded, from highest to lowest.
    Indices correspond to zoom levels.
    """

    neighbors: List[YandexPanorama] = None
    """A list of nearby panoramas."""
    links: List[Link] = None
    """The panoramas which the white arrows in the client link to."""
    historical: List[YandexPanorama] = None
    """A list of panoramas with a different date at the same location."""

    date: datetime = None
    """Capture date and time of the panorama."""
    height: float = None
    """Height above ground (not sea level) in meters."""
    street_name: str = None
    """The name of the street the panorama is located on."""

    places: List[Place] = None
    """Companies or landmarks whose markers are overlaid on this panorama."""
    addresses: List[Address] = None
    """Addresses whose markers are overlaid on this panorama."""
    other_markers: List[Marker] = None
    """Represents other markers which are neither an address, company, nor landmark."""

    author: str = None
    """Name of the uploader; only set for third-party panoramas."""
    author_avatar_url: str = None
    """URL of the uploader's avatar; only set for third-party panoramas. 
    Replace ``%s`` with ``small`` (25x25), ``normal`` (100x100) or ``big`` (500x500) to get the respective size."""

    def permalink(self: YandexPanorama, heading: float = 0.0, pitch: float = 0.0,
                  map_zoom: float = 17.0, radians: bool = True) -> str:
        """
        Creates a permalink to this panorama.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Yandex Maps URL which will open this panorama.
        """
        return build_permalink(id=self.id, lat=self.lat, lon=self.lon, heading=heading, pitch=pitch,
                               map_zoom=map_zoom, radians=radians)

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"


@dataclass
class Place:
    """A company or landmark whose marker is overlaid on the panorama."""
    id: int
    """ID of the place."""
    lat: float
    """Latitude of the place's location."""
    lon: float
    """Longitude of the place's location."""
    name: str
    """Name of the place."""
    tags: List[str]
    """Typically has one entry specifying the type of the place."""


@dataclass
class Address:
    """An address whose marker is overlaid on the panorama."""
    lat: float
    """Latitude of the address."""
    lon: float
    """Longitude of the address."""
    house_number: str
    """House number of the address."""
    street_name_and_house_number: str
    """Street name and house number of the address."""


@dataclass
class Marker:
    """A marker which is neither an address, company, nor landmark."""
    lat: float
    """Latitude of the marker."""
    lon: float
    """Longitude of the marker."""
    name: str
    """"""
    description: str
    """"""
    style: str
    """
    A link to an element in an XML document describing how the marker should be drawn.
    What the marker represents can be inferred from the ID of the element.
    """
