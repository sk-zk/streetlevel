from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from numpy import ndarray

from streetlevel.dataclasses import Size


@dataclass
class StreetViewPanorama:
    """
    Metadata of a Street View panorama.

    ID, latitude and longitude are always present. The availability of other metadata depends on which function
    was called and what was returned by the API.
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
    historical: List[StreetViewPanorama] = field(default_factory=list)
    """A list of panoramas with a different date at the same location."""

    date: CaptureDate = None
    """
    The capture date. Note that, for official coverage, only month and year are available.
    For third-party coverage, the day is available also.
    """

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
    | This can be localized using the locale parameter on the find/lookup functions (if a localization is available). 
      For instance, requesting Italian locale (``it``) for the same location as above yields:
    | ``[LocalizedString(value='3 Piazza Teatro', language='it'), LocalizedString(value='Merano, Trentino-Alto Adige', language='it')]``.
    
    Typically only set for official road coverage.
    """

    source: str = None
    """
    The source program of the imagery.

    For official coverage, ``launch`` refers to car coverage and ``scout`` refers to trekker or tripod coverage.
    (Note, however, that not all trekker coverage is marked ``scout``:
    the sidewalk trekker in Helsinki, for example, has its blue lines snapped to roads and 
    therefore returns ``launch``.)

    For third-party coverage, this returns the app the panorama was uploaded with,
    such as ``photos:street_view_android`` (the now-discontinued Street View app, RIP) or 
    ``photos:street_view_publish_api``.
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

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date.year}-{self.date.month:02d}"
            if self.date.day is not None:
                output += f"-{self.date.day:02d}"
            output += "]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6})"


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
