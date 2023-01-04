#### <code>download_panorama(<em>pano, filename, zoom=5</em>)</code>

Downloads a panorama to a file.

Supports all camera generations as well as third-party coverage.

**pano**: A `StreetViewPanorama` object.  
**filename**: Output filename.  
**zoom**: Image size; 0 is lowest, 5 is highest. The actual dimensions of the panorama depend on the camera generation used.
If the requested zoom level does not exist, the highest available level will be used.


#### <code>find_panorama(<em>lat, lon, radius=50, download_depth=False, locale="en", session=None</em>)</code>

Searches for a panorama within a radius around a point.

**lat**, **lon**: Latitude and longitude.  
**radius**: Search radius in meters.  
**download_depth**: Whether or not to download the depth map. The library does not yet parse this data, so for now, this should always be false.  
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

As above, but for fetching the tile on which a lat/lon coordinate is located.


#### <code>get_panorama(<em>pano, zoom=5</em>)</code>

Like `download_panorama()`, but the panorama is returned as a PIL image.


#### <code>is_third_party_panoid(<em>panoid</em>)</code>

Returns whether or not a pano ID refers to third-party coverage rather than official Google coverage.

**panoid**: The pano ID.


#### <code>lookup_panoid(<em>panoid, download_depth=False, locale="en", session=None</em>)</code>

Fetches metadata of a specific panorama.

**panoid**: The pano ID.  
**download_depth**: Whether or not to download the depth map. The library does not yet parse this data, so for now, this should always be false.  
**locale**: Desired language of the location's address as IETF code.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).  
