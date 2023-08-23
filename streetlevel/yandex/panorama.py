from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


from streetlevel.dataclasses import Size


@dataclass
class YandexPanorama:
    id: str
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

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
    historical: List[YandexPanorama] = None
    """A list of panoramas with a different date at the same location."""

    date: datetime = None
    """Capture date and time of the panorama."""

    street_name: str = None
    """The name of the street the panorama is located on."""

    author: str = None
    """Name of the uploader; only set for third-party panoramas."""
    author_avatar_url: str = None
    """URL of the uploader's avatar; only set for third-party panoramas. 
    Replace ``%s`` with ``small`` (25x25), ``normal`` (100x100) or ``big`` (500x500) to get the respective size."""
