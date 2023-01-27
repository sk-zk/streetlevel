from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class StreetViewPanorama:
    id: int
    lat: float
    lon: float

    day: int = None
    month: int = None
    year: int = None

    country_code: str = None
    street_name: List[str] = None
    address: List[List[str]] = None

    neighbors: List[StreetViewPanorama] = field(default_factory=list)
    historical: List[StreetViewPanorama] = field(default_factory=list)

    tile_size: List[int] = None
    image_sizes: List[List[int]] = None

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
