## StreetViewPanorama class

The StreetViewPanorama class has the following properties:

**id: *int***  
The panorama ID.

**lat/lon: *float***  
The WGS84 latitude and longitude at which the panorama was taken.

**address: *List[LocalizedString]***  
The address of the location and the languages of the names, e.g. `[LocalizedString(value='3 Theaterpl.', language='de'), LocalizedString(value='Merano, Trentino-South Tyrol', language='en')]`.
This can be localized using the `locale` parameter on the find/lookup functions (if a localization is available). For instance,
requesting Italian locale (`it`) yields `[LocalizedString(value='3 Piazza Teatro', language='it'), LocalizedString(value='Merano, Trentino-Alto Adige', language='it')]`.

Typically only set for official road coverage.

**copyright_message: *str***  
The copyright message of the panorama as displayed on Google Maps. For official coverage, this returns "© (year) Google".

**country_code: *str***  
The country in which the panorama is located.

**day/month/year: *int***  
The capture date. Note that, for official coverage, only month and year are available.

**depth: *DepthMap***  
The depth map, if it was requested. Values are in meters. -1 is used for the horizon.

**heading: *float***  
Heading in radians, where 0° is north, 90° is east, 180° is south and 270° is west.

**historical: *List[StreetViewPanorama]***  
A list of panoramas with a different date at the same location.

**image_sizes: *List[Size]***  
The image sizes in which this panorama can be downloaded, from lowest to highest.

**neighbors: *List[StreetViewPanorama]*** 
A list of nearby panoramas.

**pitch: *float***  
Pitch offset of the panorama in radians.

**roll: *float***  
Roll offset of the panorama in radians.

**source: *str***  
The source program of the imagery. For official coverage, `launch` refers to car coverage and `scout` refers to trekker or tripod coverage. (Note, however,
that not all trekker coverage is marked `scout`: the sidewalk trekker in Helsinki, for example, returns `launch`.)

For third party coverage, this returns the app the panorama was uploaded with, like `photos:street_view_android` or `photos:street_view_publish_api`

**street_name: *LocalizedString***  
The name of the street the panorama is located on, and the language of that name, e.g. `LocalizedString(value='Piazza Teatro', language='it')`.

Typically only set for official road coverage.

**tile_size: *Size***  
Street View panoramas are broken up into multiple tiles. This returns the size of one tile.

**uploader: *str***  
The creator of the panorama. For official coverage, this returns "Google".

**uploader_icon_url: *str***  
URL of the icon displayed next to the uploader on Google Maps.


## Finding panoramas

#### <code>find_panorama(<em>lat: float, lon: float, radius: int = 50, locale: str = "en", session: Session = None</em>) -> StreetViewPanorama | None</code>
Searches for a panorama within a radius around a point.

**lat**, **lon**: Latitude and longitude.  
**radius**: Search radius in meters.  
**locale**: Desired language of the location's address as IETF code.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).

#### <code>get_coverage_tile(<em>tile_x: int, tile_y: int, session: Session = None</em>) -> List[StreetViewPanorama]</code>
Fetches Street View coverage on a specific [map tile](https://developers.google.com/maps/documentation/javascript/coordinates).

When viewing Google Maps with satellite imagery in globe view and zooming into a spot, it makes this API call. This is useful because 1) it allows for fetching coverage for a whole area, and 2) there are various hidden/removed locations which cannot be found by any other method (unless you access them by pano ID directly).

Note, however, that only ID, lat and lon of the most recent coverage are returned. The rest of the metadata must be fetched manually one by one.

**tile_x**, **tile_y**: X and Y coordinate of the tile in Google Maps at zoom level 17.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).

#### <code>get_coverage_tile_by_latlon(<em>lat: float, lon: float, session: Session = None</em>) -> List[StreetViewPanorama]</code>
As above, but for fetching a tile on which a lat/lon coordinate is located.

#### <code>lookup_panoid(<em>panoid: str, download_depth: bool = False, locale: str = "en", session: Session = None</em>) -> StreetViewPanorama | None</code>
Fetches metadata of a specific panorama.

**panoid**: The pano ID.  
**download_depth**: Whether to download and parse the depth map.  
**locale**: Desired language of the location's address as IETF code.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).  


## Downloading panoramas

#### <code>download_panorama(<em>pano: StreetViewPanorama, path: str, zoom: int = 5, pil_args: dict = None</em>) -> None</code>
Downloads a panorama to a file.

Supports all camera generations as well as third-party coverage.

**pano**: The panorama.  
**path**: Output path.  
**zoom**: Image size; 0 is lowest, 5 is highest. The dimensions of a zoom level of a specific panorama depend on the camera used.  
If the requested zoom level does not exist, the highest available level will be downloaded.
**pil_args**: Additional arguments for the [`Image.save()`](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save) method, e.g. `pil_args={"quality":100}`.

#### <code>get_panorama(<em>pano: StreetViewPanorama, zoom: int = 5</em>) -> Image</code>
Like `download_panorama()`, but the panorama is returned as a PIL image.


## Misc

#### <code>is_third_party_panoid(<em>panoid: str</em>) -> bool</code>
Returns whether a pano ID points to third-party coverage rather than official Google coverage.

**panoid**: The pano ID.
