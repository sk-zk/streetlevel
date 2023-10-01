from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


from streetlevel.dataclasses import Size, Link


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

    author: str = None
    """Name of the uploader; only set for third-party panoramas."""
    author_avatar_url: str = None
    """URL of the uploader's avatar; only set for third-party panoramas. 
    Replace ``%s`` with ``small`` (25x25), ``normal`` (100x100) or ``big`` (500x500) to get the respective size."""

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"
