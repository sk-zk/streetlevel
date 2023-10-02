from dataclasses import dataclass
from typing import Any


@dataclass
class Size:
    """Represents a size."""

    x: int
    y: int


@dataclass
class Tile:
    """The coordinate and URL of one tile of a tiled panorama."""

    x: int
    """X coordinate of the tile."""
    y: int
    """Y coordinate of the tile."""
    url: str
    """URL of the tile."""


@dataclass
class Link:
    """A linked panorama."""

    pano: Any
    """The panorama."""
    direction: float
    """Angle in radians."""
