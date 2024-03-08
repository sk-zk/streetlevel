from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from streetlevel.dataclasses import Size, Link
from .util import build_permalink


@dataclass
class MapyPanorama:
    """
    Metadata of a Mapy.cz panorama.
    """

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

    links: List[Link] = field(default_factory=list)
    """The panoramas which the arrows in the client link to."""
    historical: List[MapyPanorama] = field(default_factory=list)
    """A list of panoramas with a different date at the same location."""

    def permalink(self: MapyPanorama, heading: float = 0.0, pitch: float = 0.0, fov: float = 72.0,
                  map_zoom: float = 17.0, radians: bool = False) -> str:
        """
        Creates a permalink to this panorama.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param fov: *(optional)* Initial FOV of the viewport. Defaults to 72°.
        :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Mapy.cz URL which will open the given panorama.
        """
        return build_permalink(id=self.id, lat=self.lat, lon=self.lon, heading=heading, pitch=pitch,
                               fov=fov, map_zoom=map_zoom, radians=radians)

    def __repr__(self):
        return str(self) + f" [{self.date}]"

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"
