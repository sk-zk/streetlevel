from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import List

from streetlevel.dataclasses import Link
from .util import build_permalink


class PanoramaType(IntEnum):
    """
    The panorama type and/or the camera the panorama was taken with.
    Identifiers are taken directly from the source.
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
    """
    Metadata of a Kakao Road View panorama.

    ID, latitude and longitude are always present. The availability of other metadata depends on which function
    was called and what was returned by the API.
    """

    id: int
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    heading: float = None
    """Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west."""

    wcongx: float = None
    """X coordinate of the panorama's location in the WCongnamul coordinate system."""
    wcongy: float = None
    """Y coordinate of the panorama's location in the WCongnamul coordinate system."""

    image_path: str = None
    """Part of the panorama tile URL."""

    neighbors: List[KakaoPanorama] = None
    """A list of nearby panoramas."""
    links: List[Link] = None
    """The panoramas which the white arrows in the client link to."""
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

    panorama_type: PanoramaType = None
    """
    The panorama type and/or the camera the panorama was taken with. 
    Identifiers are taken directly from the source.
    """

    @property
    def is_car(self) -> bool:
        """Whether the panorama was taken by a car."""
        return self.panorama_type in [PanoramaType.CAR, PanoramaType.NAVER_CAR, PanoramaType.INSTA_TITAN]

    def permalink(self: KakaoPanorama, heading: float = 0.0, pitch: float = 0.0, radians: bool = False) -> str:
        """
        Creates a permalink to a panorama at this location.

        The link will only work as expected for the most recent coverage at a location --
        it does not appear to be possible to directly link to older panoramas.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A KakaoMap URL.
        """
        return build_permalink(id=self.id, wcongx=self.wcongx, wcongy=self.wcongy,
                               heading=heading, pitch=pitch, radians=radians)

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.5f}, {self.lon:.5f})"
