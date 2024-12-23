from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from streetlevel.baidu.util import build_permalink
from streetlevel.dataclasses import Size


@dataclass
class BaiduPanorama:
    """
    Metadata of a Baidu Maps panorama.

    ID and capture date are always present. The availability of other metadata depends on which function
    was called and what was returned by the API.
    """
    id: str
    """The panorama ID."""
    x: float
    """BD09MC X coordinate of the panorama's location."""
    y: float
    """BD09MC Y coordinate of the panorama's location."""
    elevation: float = None
    """Elevation at the capture location in meters. May be 0 for interiors/tripods or user-provided footage."""
    lat: float = None
    """WGS84 latitude of the panorama's location."""
    lon: float = None
    """WGS84 longitude of the panorama's location."""

    heading: float = None
    """Heading of the car in radians, where 0° is north, 90° is east, 180° is south, and 270° is west."""
    pitch: float = None
    """Pitch offset for upright correction of the panorama, in radians."""
    roll: float = None
    """Roll offset for upright correction of the panorama, in radians."""

    neighbors: List[BaiduPanorama] = None
    """A list of nearby panoramas."""
    historical: List[BaiduPanorama] = None
    """A list of panoramas with a different date at the same location. Note that ID, capture date
    and provider are the only set fields."""

    date: datetime = None
    """The capture date and time in UTC+8."""
    height: float = None
    """Camera height above ground (not sea level) in meters. May be 0 for user-provided panoramas."""
    street_name: str = None
    """The street name."""

    provider: Union[Provider, int] = None
    """The company or organisation which captured the panorama. If the enum value returned by the API is known,
    this field is of type ``Provider``. Otherwise, it contains the raw integer."""
    creator: Optional[User] = None
    """Name and ID of the uploader if this is a user-provided panorama."""

    interior: Optional[PanoInteriorMetadata] = None
    """
    If this panorama is part of a set of interior/tripod (``inter``) panoramas,
    this object contains metadata of the PoI and all other panoramas in the set.
    """

    @property
    def tile_size(self) -> Size:
        """
        Baidu panoramas are broken up into a grid of tiles. This returns the size of one tile.
        """
        return Size(512, 512)

    image_sizes: List[Size] = None
    """
    The image sizes in which this panorama can be downloaded, from lowest to highest.
    Indices correspond to zoom levels.
    """

    def permalink(self: BaiduPanorama, heading: float = 0.0, pitch: float = 0.0, radians: bool = False) -> str:
        """
        Creates a permalink to this panorama.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Baidu Maps URL pointing to this panorama.
        """
        return build_permalink(id=self.id, heading=heading, pitch=pitch, radians=radians)

    def __repr__(self):
        if self.date:
            return str(self) + f" [{self.date}]"
        else:
            return str(self)

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"


@dataclass
class PanoInteriorMetadata:
    """
    Metadata of a set of interior/tripod (``inter``) panoramas
    as returned by the API call made by ``find_panorama_by_id``.
    """
    id: str
    """The IID identifying the set of panoramas at this PoI."""
    name: str
    """The name of the PoI."""
    exit_panoid: str
    """The ID of a regular panorama which is loaded upon exiting the building."""
    uid: str
    """The UID of the PoI."""
    panos: List[PanoInteriorPoint]
    """All panoramas of this location."""
    x: Optional[float] = None
    """BD09MC X coordinate of the PoI's location, if available."""
    y: Optional[float] = None
    """BD09MC Y coordinate of the PoI's location, if available."""
    lat: Optional[float] = None
    """WGS84 latitude of the PoI's location, if available."""
    lon: Optional[float] = None
    """WGS84 longitude of the PoI's location, if available."""


@dataclass
class PanoInteriorPoint:
    """
    Metadata of an interior/tripod (``inter``) panorama
    as returned by the API call made by ``find_panorama_by_id``.
    """
    id: str
    """The panorama ID."""
    name: str
    """The name of the panorama, typically describing its location."""
    floor: int
    """The floor on which the panorama is located."""
    date: datetime
    """The capture date and time in UTC+8."""


@dataclass
class InteriorMetadata:
    """
    Metadata of a set of interior/tripod (``inter``) panoramas as returned by the
    API call made by ``get_inter_metadata``.
    """
    id: str
    """The IID identifying the set of panoramas at this PoI."""
    name: str
    """The name of the PoI."""
    uid: str
    """The UID of the PoI."""
    x: float
    """BD09MC X coordinate of the PoI's location."""
    y: float
    """BD09MC Y coordinate of the PoI's location."""
    lat: float
    """WGS84 latitude of the PoI's location."""
    lon: float
    """WGS84 longitude of the PoI's location."""
    floors: List[Floor]
    """The floors of this location and the panoramas located on them."""
    default_floor: int
    """The floor which is shown first."""
    exit_pano: Optional[BaiduPanorama]
    """The panorama which is loaded upon exiting the building."""


@dataclass
class Floor:
    """
    One floor of a set of interior/tripod (``inter``) coverage as returned by the
    API call made by ``get_inter_metadata``.
    """
    number: int
    """The floor number."""
    name: str
    """The name of the floor."""
    start_panoid: str
    """The ID of the initial pano to display for this floor."""
    panos: List[InteriorPoint]
    """Panoramas on this floor."""


@dataclass
class InteriorPoint:
    """
    One panorma of a set of interior/tripod (``inter``) coverage as returned by the
    API call made by ``get_inter_metadata``.
    """
    name: str
    """The name of the panorama, typically describing its location."""
    floor: int
    """The floor on which the panorama is located."""
    creator: Optional[str]
    """The name of the uploader if this is a user-provided panorama."""
    catalog_label: str
    """The room type."""
    pano: BaiduPanorama
    """The panorama metadata."""


@dataclass
class User:
    """
    Name and ID of a Baidu user.
    """
    id: str
    """ID of the user. Not always available."""
    name: str
    """Name of the user."""


class Provider(Enum):
    """
    The provider of a Baidu Maps panorama.
    """
    BAIDU = 0
    """The panorama was captured by Baidu or a user of Baidu."""
    CITY8 = 1
    """城市吧 (City8, city8.com)"""
    LIDE_SPACE = 2
    """立得空间 (LIDE Space)"""
    VRWAY = 3
    """全瑞景 (VRWay Communication, vrlooking.com)"""
    TAAGOO = 4
    """互动世界 (taagoo.com)"""
    ZHDGPS = 5
    """都市圈 (Guangzhou Zhonghaida Satellite Navigation Technology, zhdgps.com)"""
    PEACEMAP = 6
    """天下图 (Tianxiatu, peacemap.com.cn)"""
    TMIC = 7
    """时间机器 (Time Machine Cultural Communication, chinatmic.com)"""
    SUPER720 = 11
    """方位科技有限公司 (Super720, super720.com)"""
    PANORAMA_NETWORK = 12
    """中国全景网 (China Panorama Network, vra.cn)"""
    TIANYA = 13
    """海南丽声 (Hainan Lisheng, tianya.tv)"""
