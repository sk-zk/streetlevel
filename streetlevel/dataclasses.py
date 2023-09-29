from dataclasses import dataclass


@dataclass
class Size:
    x: int
    y: int


@dataclass
class Tile:
    """Represents the coordinate and URL of one tile of a tiled panorama."""

    x: int
    """X coordinate of the tile."""
    y: int
    """Y coordinate of the tile."""
    url: str
    """URL of the tile."""


@dataclass
class Link:
    """
    A linked panorama.
    """
    pano: any
    """The panorama."""
    direction: float
    """Angle in radians."""
