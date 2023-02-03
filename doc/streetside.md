## StreetsidePanorama class

The StreetsidePanorama class has the following properties:

**id: *int***  
The panorama ID.

**lat/lon: *float***  
The WGS84 latitude and longitude at which the panorama was taken.

**date: *datetime***  
The capture date.

**elevation: *int***  
Elevation in meters.

**heading: *float***  
Heading of the car in radians, where 0° is north, 90° is east, 180° is south and 270° is west.

**next: *int***  
ID of the next image in the sequence.

**pitch: *float***  
Pitch offset of the panorama in radians.

**previous: *int***  
ID of the previous image in the sequence.

**roll: *float***  
Roll offset of the panorama in radians.


## Finding panoramas

#### <code>find_panoramas(<em>lat: float, lon: float, radius: float = 25, limit: int = 50, session: Session = None</em>) -> List[StreetsidePanorama]</code>
Retrieves panoramas within a square around a point.

**lat**, **lon**: Latitude and longitude of the center point.  
**radius**: Radius of the square in meters. (Not sure if that's the correct mathematical term, but you get the idea.)  
**limit**: Maximum number of results to return.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).

#### <code>find_panoramas_in_bbox(<em>north: float, west: float, south: float, east: float, limit: int = 50, session: Session = None</em>) -> List[StreetsidePanorama]</code>
Retrieves panoramas within a bounding box.

**north**, **west**: lat1/lon1.  
**south**, **east**: lat2/lon2.  
**limit**: Maximum number of results to return.  
**session**: A [session object](https://docs.python-requests.org/en/master/user/advanced/#session-objects).


## Downloading panoramas

#### <code>download_panorama(<em>panoid: int, path: str, zoom: int = 3, single_image: bool = True, pil_args: dict = None</em>) -> None</code>
Downloads a panorama to a file.

**panoid**: The pano ID.  
**path**: Output path.  
**zoom**: Image size; 0 is lowest, 3 is highest.  
**single_image**: Whether to output a single image or six indiviual images.
**pil_args**: Additional arguments for the [`Image.save()`](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save) method, e.g. `pil_args={"quality":100}`.

#### <code>get_panorama(<em>panoid: int, zoom: int = 3, single_image: bool = True</em>) -> Image | List[Image] </code>
Like `download_panorama()`, but the panorama is returned as a PIL image.

## Misc

#### <code>from_base4(<em>n: str</em>) -> int</code>
Converts a string containing a base 4 number to integer.

#### <code>to_base4(<em>n: int</em>) -> str</code>
Converts an int to a base 4 string.
