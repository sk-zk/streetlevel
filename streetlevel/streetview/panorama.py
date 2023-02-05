from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from numpy import ndarray

from streetlevel.dataclasses import Size


@dataclass
class StreetViewPanorama:
    id: int
    lat: float
    lon: float

    heading: float = None
    pitch: float = None
    roll: float = None
    depth: DepthMap = None

    tile_size: Size = None
    image_sizes: List[Size] = None

    neighbors: List[StreetViewPanorama] = field(default_factory=list)
    historical: List[StreetViewPanorama] = field(default_factory=list)

    day: int = None
    month: int = None
    year: int = None

    country_code: str = None
    street_name: LocalizedString = None
    address: List[LocalizedString] = None

    source: str = None

    copyright_message: str = None
    uploader: str = None
    uploader_icon_url: str = None

    def __repr__(self):
        output = str(self)
        if self.year is not None and self.month is not None:
            output += f" [{self.year}-{self.month:02d}"
            if self.day is not None:
                output += f"-{self.day:02d}"
            output += "]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6})"


@dataclass
class LocalizedString:
    value: str
    language: str


@dataclass
class DepthMap:
    width: int
    height: int
    data: ndarray
