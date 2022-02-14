#### <code>download_panorama(<em>panoid, directory, zoom=3</em>)</code>

Downloads a panorama and saves it in the given directory. The pano ID will be used as filename.

**panoid**: The pano ID.  
**directory**: The output directory.  
**zoom**: Image size; 0 is lowest, 3 is highest.


#### <code>find_panoramas(<em>north, west, south, east, limit=50</em>):</code>

Retrieves panoramas within a rectangle.

**north**, **west**: lat1/lon1.  
**south**, **east**: lat2/lon2.  
**limit**: Maximum number of results to return.


#### <code>from_base4(<em>n</em>)</code>

Converts a string containing a base 4 number to integer.


#### <code>get_panorama(<em>panoid, zoom=3</em>)</code>

Like `download_panorama()`, but the panorama is returned as a PIL image.


#### <code>to_base4(<em>n</em>)</code>

Converts an int to a base 4 string.