#### <code>download_panorama(<em>panoid, directory, zoom=3</em>)</code>

Downloads a panorama and saves it in the given directory. The pano ID will be used as filename.

**panoid**: The pano ID.  
**directory**: The output directory.  
**zoom**: Image size; 0 is lowest, 3 is highest.


#### <code>find_panoramas(<em>lat, lon, radius=25, limit=50, session=None</em>)</code>

Retrieves panoramas within a square around a point.

**lat**, **lon**: Latitude and longitude of the center point.  
**radius**: Radius of the square in meters. (Not sure if that's the correct mathematical term, but you get the idea.)  
**limit**: Maximum number of results to return.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).


#### <code>find_panoramas_in_rectangle(<em>north, west, south, east, limit=50, session=None</em>)</code>

Retrieves panoramas within a rectangle.

**north**, **west**: lat1/lon1.  
**south**, **east**: lat2/lon2.  
**limit**: Maximum number of results to return. 
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).


#### <code>from_base4(<em>n</em>)</code>

Converts a string containing a base 4 number to integer.


#### <code>get_panorama(<em>panoid, zoom=3</em>)</code>

Like `download_panorama()`, but the panorama is returned as a PIL image.


#### <code>to_base4(<em>n</em>)</code>

Converts an int to a base 4 string.