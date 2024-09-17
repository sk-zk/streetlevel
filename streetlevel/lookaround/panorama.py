from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple, List

from streetlevel.lookaround import geo
from .util import build_permalink


class CoverageType(Enum):
    """
    Coverage type of a Look Around panorama.
    """
    CAR = 2
    """
    The panorama was taken by a car.
    """
    BACKPACK = 3
    """
    The panorama was taken by a backpack.
    """


@dataclass
class LookaroundPanorama:
    """
    Metadata of a Look Around panorama.
    """

    id: int
    """The pano ID."""
    build_id: int
    """
    An additional parameter required for requesting the imagery. Each time Apple publishes or updates 
    a set of panoramas, they are assigned a build ID to act as a revision number.
    """

    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    coverage_type: CoverageType = None
    """Whether the coverage was taken by car or by backpack."""
    date: datetime = None
    """Capture date and time of the panorama (in UTC, not local time)."""

    has_blurs: bool = None
    """Whether something in this panorama, typically a building, has been blurred."""

    raw_orientation: Tuple[int, int, int] = None
    """The raw yaw, pitch, and roll values returned by the API."""

    raw_altitude: int = None
    """The raw altitude value returned by the API."""

    tile: Tuple[int, int, int] = None
    """The tile this panorama is located on."""

    camera_metadata: List[CameraMetadata] = None
    """Properties needed for rendering the panorama faces."""

    _heading: float = None
    _pitch: float = None
    _roll: float = None
    _elevation: float = None
    _altitude: float = None

    def _set_altitude_and_elevation(self):
        if not self._elevation:
            self._altitude, self._elevation = \
                geo.convert_altitude(self.raw_altitude, self.lat, self.lon, self.tile[0], self.tile[1])

    def _set_orientation(self):
        if not self._heading:
            self._heading, self._pitch, self._roll = \
                geo.convert_pano_orientation(self.lat, self.lon, *self.raw_orientation)

    @property
    def elevation(self) -> float:
        """Elevation at the capture location in meters."""
        self._set_altitude_and_elevation()
        return self._elevation

    @property
    def heading(self) -> float:
        """
        Heading in radians, where 0° is north, 90° is west, 180° is south, 270° is east.
        """
        self._set_orientation()
        return self._heading

    @property
    def pitch(self) -> float:
        """Pitch offset for upright correction of the panorama, in radians."""
        self._set_orientation()
        return self._pitch

    @property
    def roll(self) -> float:
        """Roll offset for upright correction of the panorama, in radians."""
        self._set_orientation()
        return self._roll

    def permalink(self: LookaroundPanorama, heading: float = 0.0, pitch: float = 0.0, radians: bool = False) -> str:
        """
        Creates a link which will open a panorama at this location in Apple Maps.
        Linking to a specific panorama by its ID does not appear to be possible.

        On non-Apple devices, the link will redirect to Google Maps.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 0°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: An Apple Maps URL which will open the closest panorama to this location.
        """
        return build_permalink(self.lat, self.lon, heading=heading, pitch=pitch, radians=radians)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id}/{self.build_id} ({self.lat:.5f}, {self.lon:.5f})"


@dataclass
class CameraMetadata:
    lens_projection: LensProjection  #:
    position: OrientedPosition  #:


@dataclass
class LensProjection:
    fov_s: float
    """Phi size of the panorama face."""
    fov_h: float
    """Theta size of the panorama face."""
    k2: float  #:
    k3: float  #:
    k4: float  #:
    cx: float
    """Theta offset."""
    cy: float
    """Phi offset."""
    lx: float  #:
    ly: float  #:


@dataclass
class OrientedPosition:
    """Position and rotation of a panorama face in the scene. Angles are in radians."""
    x: float  #:
    y: float  #:
    z: float  #:
    yaw: float  #:
    pitch: float  #:
    roll: float  #:


@dataclass
class CoverageTile:
    """Represents a coverage tile."""
    x: int
    """The X coordinate of the tile at z=17."""
    y: int
    """The Y coordinate of the tile at z=17."""
    panos: List[LookaroundPanorama]
    """Panoramas on this tile."""
    last_modified: datetime
    """
    The time the tile was last changed. This happens whenever footage is published or removed, 
    new blurs are applied, or (I assume) PoIs are updated.
    """
