from dataclasses import dataclass
from enum import Enum


class CoverageType(Enum):
    CAR = 2
    BACKPACK = 3


@dataclass
class LookaroundPanorama:
    id: int
    region_id: int
    lat: float
    lon: float
    heading: float = None
    coverage_type: CoverageType = None
    timestamp: int = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id}/{self.region_id} ({self.lat:.6}, {self.lon:.6})"
