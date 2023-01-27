## StreetViewPanorama class

The StreetViewPanorama class has the following properties:

**id**:  
The panorama ID.

**lat/lon**:  
The WGS84 latitude and longitude at which the panorama was taken.

**address**:  
The address of the location and the languages of the names, e.g. `[['39 Obertaler Str.', 'de'], ['Trentino-South Tyrol', 'en']]`.
This can be localized using the `locale` parameter on the find/lookup functions (if a localization is available). For instance,
requesting Danish locale (`da`) would yield `[['39 Obertaler Str.', 'de'], ['Trentino-Sydtyrol', 'da']]`.

Typically only set for official road coverage.

**copyright_message**:  
The copyright message of the panorama as displayed on Google Maps. For official coverage, this will say "© (year) Google".

**country_code**:  
The country in which the panorama is located.

**day/month/year**:  
The capture date. Note that, for official coverage, only month and year are available.

**historical**:  
A list of panoramas with a different date at the same location.

**image_sizes**:  
The image sizes in which this panorama can be downloaded, from lowest to highest.

**neighbors**:  
A list of nearby panoramas.

**source**:  
The source program of the imagery. For official coverage, `launch` refers to car coverage and `scout` refers to trekker or tripod coverage. (Note, however,
that not all trekker coverage is marked `scout`: the sidewalk trekker in Helsinki, for example, returns `launch`.)

For third party coverage, this returns the app the panorama was uploaded with.

**street_name**:  
The name of the street the panorama is located on, and the language of that name, e.g. `['Obertaler Str.', 'de']`.

Typically only set for official road coverage.

**tile_size**:  
Street View panoramas are broken up into multiple tiles. This returns the size of one tile.

**uploader**:  
The creator of the panorama. For official coverage, this will say "Google".

**uploader_icon_url**:  
URL to the icon displayed next to the uploader on Google Maps.


## Finding panoramas

#### <code>find_panorama(<em>lat, lon, radius=50, download_depth=False, locale="en", session=None</em>)</code>
Searches for a panorama within a radius around a point.

**lat**, **lon**: Latitude and longitude.  
**radius**: Search radius in meters.  
**download_depth**: Whether to download the depth map. The library does not yet parse this data, so for now, this should always be false.  
**locale**: Desired language of the location's address as IETF code.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).

#### <code>get_coverage_tile(<em>tile_x, tile_y, session=None</em>)</code>
Fetches Street View coverage on a specific [map tile](https://developers.google.com/maps/documentation/javascript/coordinates).

When viewing Google Maps with satellite imagery in globe view and zooming into a spot, it calls the API method
which is called here. This is useful because there are various hidden/removed locations which cannot be found by
any other method (unless you access them by pano ID directly).

**tile_x**, **tile_y**: X and Y coordinate of the tile in Google Maps at zoom level 17.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).

#### <code>get_coverage_tile_by_latlon(<em>lat, lon, session=None</em>):</code>
As above, but for fetching a tile on which a lat/lon coordinate is located.

#### <code>lookup_panoid(<em>panoid, download_depth=False, locale="en", session=None</em>)</code>
Fetches metadata of a specific panorama.

**panoid**: The pano ID.  
**download_depth**: Whether or not to download the depth map. The library does not yet parse this data, so for now, this should always be false.  
**locale**: Desired language of the location's address as IETF code.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).  


## Downloading panoramas

#### <code>download_panorama(<em>pano, path, zoom=5</em>)</code>
Downloads a panorama to a file.

Supports all camera generations as well as third-party coverage.

**pano**: A `StreetViewPanorama` object.  
**path**: Output path.  
**zoom**: Image size; 0 is lowest, 5 is highest. The dimensions of a zoom level of a specific panorama depend on the camera used.
If the requested zoom level does not exist, the highest available level will be downloaded.

#### <code>get_panorama(<em>pano, zoom=5</em>)</code>
Like `download_panorama()`, but the panorama is returned as a PIL image.


## Misc

#### <code>is_third_party_panoid(<em>panoid</em>)</code>
Returns whether a pano ID points to third-party coverage rather than official Google coverage.

**panoid**: The pano ID.
