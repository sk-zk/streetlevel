from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List


class CameraType(IntEnum):
    """
    The camera a panorama was captured with. Identifiers are taken directly from ``panorama.js``.
    """
    PANOZIP = 100,  #:
    ROTATOR = 101,  #:
    CAR = 102,  #:
    SKY = 103,  #:
    NAVER_CAR = 200,  #:
    INSTA360 = 201,  #:
    INSTA_TITAN = 202,  #:
    SEA = 203,  #:
    SDMG_OFFICE = 204  #:


@dataclass
class KakaoPanorama:
    """Metadata of a Kakao Road View panorama."""

    id: int
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    heading: float = None
    """Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west."""

    image_path: str = None
    """Part of the panorama tile URL."""

    neighbors: List[KakaoPanorama] = None
    """A list of nearby panoramas."""
    historical: List[KakaoPanorama] = None
    """A list of panoramas with a different date at the same location. 
    Only available if the panorama was retrieved by ``find_panorama_by_id``."""

    date: datetime = None
    """Capture date and time of the panorama in UTC."""

    street_name: str = None
    """The street name as overlaid on the road in the panorama viewer."""
    address: str = None
    """The address of the location as shown in the top-left corner in the panorama viewer."""
    street_type: str = None
    """The street type (in Korean), e.g. "이면도로" (side road)."""

    camera_type: CameraType = None
    """The camera the panorama was taken with. Identifiers are taken directly from the source."""

    @property
    def is_car(self) -> bool:
        """Whether the panorama was taken by a car."""
        return self.camera_type in [CameraType.CAR, CameraType.NAVER_CAR, CameraType.INSTA_TITAN]

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"

