from dataclasses import dataclass
from datetime import datetime


@dataclass
class StreetsidePanorama:
    id: int
    lat: float
    lon: float
    date: datetime
    next: int = None
    previous: int = None
    elevation: int = None
    heading: float = None
    pitch: float = None
    roll: float = None

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6})"
