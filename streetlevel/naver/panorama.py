from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import List, Optional

import numpy as np

from streetlevel.dataclasses import Link, Size
from .util import build_permalink


class PanoramaType(IntEnum):
    """
    The panorama type. Most identifiers are taken directly from the source.
    """
    ALL = 0  #:
    AIR = 1  #:
    DRONE = 2  #:
    CAR = 3  #:
    BICYCLE = 4  #:
    MUSEUM = 5  #:
    PENSION = 7  #:
    PENSION_FRONT = 8  #:
    INDOOR = 10  #:
    INDOOR_HIGH = 11  #:
    UNDERWATER = 12  #:
    TREKKER = 13  #:
    MESH_EQUIRECT = 15
    """
    An Apple-like panorama which can be fetched in equirectangular projection
    and for which a 3D mesh is available.
    """
    INDOOR_3D = 100  #:


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
    altitude: float = None
    """Altitude of the camera above sea level, in meters."""
    pitch: float = None
    """
    Pitch offset for upright correction of the panorama, in radians. 
    Only available if ``has_equirect`` is True; the field is set to 0 otherwise.
    """
    roll: float = None
    """
    Roll offset for upright correction of the panorama, in radians. 
    Only available if ``has_equirect`` is True; the field is set to 0 otherwise.
    """

    max_zoom: int = None
    """Highest zoom level available for this panorama."""

    neighbors: Neighbors = None
    """A list of nearby panoramas."""
    links: List[Link] = None
    """
    The panoramas which the white dots in the pre-3D client link to.
    This appears to be unused in the new client.
    """
    historical: List[NaverPanorama] = None
    """A list of panoramas with a different date at the same location. 
    Only available if the panorama was retrieved by ``find_panorama_by_id``."""
    timeline_id: str = None
    """The pano ID that must be given to the API to retrieve the full list of historical panoramas, which is also
    the ID of the most recent panorama at this location. If an earlier ID is used, only panoramas up to that 
    panorama's capture date are returned."""

    date: datetime = None
    """Capture date and time of the panorama in UTC."""
    is_latest: bool = None
    """Whether this is the most recent panorama at its location."""

    description: str = None
    """The description field, which typically contains the neighborhood and city."""
    title: str = None
    """The title field, which typically contains the street name."""

    depth: np.ndarray = None
    """The legacy depth maps of the cubemap faces."""

    has_equirect: bool = None
    """
    If True, this panorama can be fetched as either in equirectangular projection or as a cubemap.
    If False, only a cubemap is available.
    """
    panorama_type: PanoramaType = None
    """The panorama type. Most identifiers are taken directly from the source."""
    overlay: Optional[Overlay] = None
    """
    Curiously, in non-3D imagery, Naver masks their car twice: once with an image of a car baked into the panorama, 
    and additionally with an image of the road beneath it (like Google and Apple), which is served as a separate file 
    and overlaid on the panorama in the client. This is the URL to that secondary overlay.
    
    (Only available for non-3D car footage.)
    """

    @property
    def tile_size(self) -> Size:
        """
        Naver panoramas in equirectangular format are broken up into a grid of tiles.
        This returns the size of one tile.
        """
        return Size(512, 512)

    def permalink(self: NaverPanorama, heading: float = 0.0, pitch: float = 10.0, fov: float = 80.0,
                  map_zoom: float = 17.0, radians: bool = False) -> str:
        """
        Creates a permalink to this panorama.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 10°.
        :param fov: *(optional)* Initial FOV of the viewport. Defaults to 80°.
        :param map_zoom: *(optional)* Initial zoom level of the map. Defaults to 17.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Naver Map URL which will open this panorama.
        """
        return build_permalink(self.id, heading=heading, pitch=pitch, fov=fov,
                               map_zoom=map_zoom, radians=radians)

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
