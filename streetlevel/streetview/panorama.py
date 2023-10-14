from __future__ import annotations
from enum import Enum

import math
from dataclasses import dataclass, field
from typing import List, Optional

from numpy import ndarray

from streetlevel.dataclasses import Size, Link
from .util import is_third_party_panoid


@dataclass
class StreetViewPanorama:
    """
    Metadata of a Street View panorama.

    ID, latitude and longitude are always present*. The availability of other metadata depends on which function
    was called and what was returned by the API.

    \*) Except for rare edge cases where latitude and longitude of links are not returned by the API and therefore
    set to None.
    """
    id: str
    """The pano ID."""
    lat: float
    """Latitude of the panorama's location."""
    lon: float
    """Longitude of the panorama's location."""

    heading: float = None
    """Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west."""

    pitch: float = None
    """Pitch offset for upright correction of the panorama, in radians."""
    roll: float = None
    """Roll offset for upright correction of the panorama, in radians."""

    depth: DepthMap = None
    """The depth map, if it was requested. Values are in meters. -1 is used for the horizon."""

    tile_size: Size = None
    """
    Street View panoramas are broken up into a grid of tiles. This returns the size of one tile.
    """
    image_sizes: List[Size] = None
    """
    The image sizes in which this panorama can be downloaded, from lowest to highest.
    Indices correspond to zoom levels.
    """

    neighbors: List[StreetViewPanorama] = field(default_factory=list)
    """A list of nearby panoramas."""
    links: List[Link] = field(default_factory=list)
    """The panoramas which the white arrows in the client link to."""
    historical: List[StreetViewPanorama] = field(default_factory=list)
    """A list of panoramas with a different date at the same location."""

    building_level: BuildingLevel = None
    """The level on which the panorama was taken (if the panorama is located inside a building which has been
    covered on multiple floors and this metadata is available)."""
    building_levels: List[StreetViewPanorama] = field(default_factory=list)
    """One panorama per floor above or below this one (if the panorama is located inside a building which has been
    covered on multiple floors and this metadata is available)."""

    date: CaptureDate = None
    """
    The capture date. Note that, for official coverage, only month and year are available.
    For third-party panoramas, the day is available also.
    """
    upload_date: UploadDate = None
    """
    The upload date. Only available for third-party panoramas.
    """

    elevation: float = None
    """Elevation at the capture location in meters."""

    country_code: str = None
    """Two-letter country code for the country in which the panorama is located."""
    street_name: LocalizedString = None
    """
    | The name of the street the panorama is located on and the language of that name, e.g.
    | ``LocalizedString(value='Piazza Teatro', language='it')``.
    
    Typically only set for official road coverage.
    """
    address: List[LocalizedString] = None
    """
    | The address of the location and the languages of the names, e.g.:
    | ``[LocalizedString(value='3 Theaterpl.', language='de'), LocalizedString(value='Merano, Trentino-South Tyrol', language='en')]``.
    |
    | This can be localized using the locale parameter on the `find` functions (if the string is available 
      in that language). 
      For instance, requesting Italian locale (``it``) for the same location as above yields:
    | ``[LocalizedString(value='3 Piazza Teatro', language='it'), LocalizedString(value='Merano, Trentino-Alto Adige', language='it')]``.
    
    Typically only set for official road coverage.
    """

    places: Optional[List[Place]] = None
    """
    If ``source`` is ``launch``, this includes buildings, businesses etc. that are visible in the panorama, 
    or intersections, addresses, etc. at the panorama's location.
    
    If ``source`` is ``scout``, ``innerspace`` or ``cultural_institute``, this (usually) contains a single element, 
    with the building or other location that the coverage is of.
    """

    source: str = None
    """
    The source program of the imagery.

    For official coverage, common values are:

    * ``launch``: regular car coverage (and sometimes trekker coverage) whose lines are snapped to roads 
    * ``scout``: trekker or tripod coverage (and sometimes car coverage) whose lines are not snapped to roads
    * ``innerspace``: tripods from Google's `Business View <https://en.wikipedia.org/wiki/Street_View_Trusted>`_ program
    * ``cultural_institute``: some (but not all) tripods from the Arts & Culture program have this value
    
    For third-party coverage, this returns the app the panorama was uploaded with, such as:
    
    * ``photos:street_view_android``, ``photos:street_view_ios``: the now-discontinued Street View app, RIP
    * ``photos:street_view_publish_api``: the `Publish API <https://developers.google.com/streetview/publish>`_
    * ``photos:legacy_innerspace``: see above
    """

    copyright_message: str = None
    """
    The copyright message of the panorama as displayed on Google Maps.
    For official coverage, this returns "© (year) Google".
    """
    uploader: str = None
    """The creator of the panorama. For official coverage, this returns "Google"."""
    uploader_icon_url: str = None
    """URL of the icon displayed next to the uploader's name on Google Maps."""

    @property
    def is_third_party(self) -> bool:
        """Whether this panorama was uploaded by a third party rather than Google."""
        return is_third_party_panoid(self.id)

    def permalink(self: StreetViewPanorama, heading: float = 0.0, pitch: float = 90.0, fov: float = 75.0,
                  radians: bool = False) -> str:
        """
        Creates a permalink to this panorama.

        :param heading: *(optional)* Initial heading of the viewport. Defaults to 0°.
        :param pitch: *(optional)* Initial pitch of the viewport. Defaults to 90°.
        :param fov: *(optional)* Initial FOV of the viewport. Defaults to 75°.
        :param radians: *(optional)* Whether angles are in radians. Defaults to False.
        :return: A Google Maps URL.
        """
        if radians:
            heading = math.degrees(heading)
            pitch = math.degrees(pitch)
            fov = math.degrees(fov)
        return f"https://www.google.com/maps/@{self.lat},{self.lon},3a,{fov}y,{heading}h,{pitch}t" \
               f"/data=!3m4!1e1!3m2!1s{self.id}!2e{10 if self.is_third_party else 0}"

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date.year}-{self.date.month:02d}"
            if self.date.day is not None:
                output += f"-{self.date.day:02d}"
            output += "]"
        return output

    def __str__(self):
        output = f"{self.id}"
        if self.lat and self.lon:
            output += f" ({self.lat:.5f}, {self.lon:.5f})"
        return output


@dataclass
class LocalizedString:
    """
    A string and a language code for the language the string is in.
    """
    value: str
    """The string."""
    language: str
    """The language code."""


@dataclass
class DepthMap:
    """
    Holds a depth map of a Street View panorama.
    """
    width: int
    """Width of the depth map."""
    height: int
    """Height of the depth map."""
    data: ndarray
    """The depth map. Values are in meters. -1 is used for the horizon."""


@dataclass
class CaptureDate:
    """
    Capture date of a Street View panorama.
    """
    year: int
    """The year the panorama was taken."""
    month: int
    """The month the panorama was taken."""
    day: int = None
    """The day the panorama was taken. Only available for third-party panoramas."""


@dataclass
class UploadDate:
    """
    Upload date of a third-party Street View panorama.
    """
    year: int  #:
    month: int  #:
    day: int  #:
    hour: int  #:


@dataclass
class BuildingLevel:
    """
    Building level of an indoor tripod Street View panorama.
    """
    level: float
    """The building level, where 0 is the ground floor, positive levels are above ground, and negative levels
    are below ground."""
    name: LocalizedString
    """Name of the level."""
    short_name: LocalizedString
    """Short name of the level."""


class BusinessStatus(Enum):
    """
    Status of a place.
    """
    Operational = 2  #:
    TemporarilyClosed = 3  #:
    PermanentlyClosed = 4  #:


@dataclass
class Place:
    """
    A place associated with a Street View panorama.
    """
    id: str
    """An ID for this place used in Google Maps URLs and internal API calls."""
    # map_node_id: Optional[int]
    marker_yaw: Optional[float]
    """Yaw of the marker's position in the panorama in radians, if a marker is returned for this place.
    This value is relative to the panorama."""
    marker_pitch: Optional[float]
    """Pitch of the marker's position in the panorama in radians, if a marker is returned for this place."""
    marker_distance: Optional[float]
    """Presumably the distance of the marker to the camera in meters."""
    name: Optional[LocalizedString]
    """Name of this place. This can be None, e.g. if type is "Geocoded address" or "Intersection"."""
    type: LocalizedString
    """Type of this place."""
    status: BusinessStatus
    """Operational status of the place. This will be ``Operational`` for locations that are not a business."""
