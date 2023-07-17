from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from streetlevel.dataclasses import Size


@dataclass
class MapyPanorama:
    id: int
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    tile_size: Size
    """Mapy panoramas are broken up into a grid of tiles. This returns the size of one tile."""
    max_zoom: int
    """Highest zoom level available; either 1 or 2."""

    domain_prefix: str
    """Part of the panorama tile URL."""
    uri_path: str
    """Part of the panorama tile URL."""
    file_mask: str
    """Part of the panorama tile URL."""

    date: datetime
    """Capture date and time of the panorama."""
    elevation: float
    """Elevation at the capture location in meters."""
    provider: str
    """The name of the company which created the panorama."""

    num_tiles: List[Size] = None

    heading: float = None
    """Heading offset in radians, where 0° is north, 90° is east, -180°/180° is south, and -90° is west."""

    omega: float = None
    """ """
    phi: float = None
    """ """
    kappa: float = None
    """ """

    pitch: float = None
    """Pitch offset for upright correction of the panorama, in radians."""
    roll: float = None
    """Roll offset for upright correction of the panorama, in radians."""

    neighbors: List[MapyPanorama] = field(default_factory=list)
    """A list of nearby panoramas."""
    historical: List[MapyPanorama] = field(default_factory=list)
    """A list of panoramas with a different date at the same location."""

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6}) [{self.date}]"
