from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MapyPanorama:
    id: int
    lat: float
    lon: float

    tile_size: list[int]
    max_zoom: int
    domain_prefix: str
    uri_path: str
    file_mask: str

    date: datetime
    elevation: float

    provider: str

    num_tiles: list[list[int]] = None

    heading: float = None
    omega: float = None
    phi: float = None
    kappa: float = None

    neighbors: list[MapyPanorama] = field(default_factory=list)
    historical: list[MapyPanorama] = field(default_factory=list)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6}) [{self.date}]"
