## MapyPanorama class

The MapyPanorama class has the following properties:

**id: *int***  
The panorama ID.

**lat/lon: *float***  
The WGS84 latitude and longitude at which the panorama was taken.

**date: *datetime***  
The capture date and time.

**domain_prefix: *str***  
Part of the panorama tile URL.

**elevation: *float***  
Elevation in meters.

**file_mask: *str***  
Part of the panorama tile URL.

**heading: *float***  
Heading offset in radians, where 0° is north, 90° is east, -180°/180° is south, and -90° is west.

**historical: *List[MapyPanorama]***  
A list of panoramas with a different date at the same location.

**max_zoom: *int***  
Highest zoom level available; either 1 or 2.

**neighbors: *List[MapyPanorama]***  
A list of nearby panoramas.

**num_tiles: *List[Size]***  
Amount of columns and rows of tiles for each zoom level.

**omega/phi/kappa: *float***  
Some kind of photogrammetry format for angles, in radians. Look, I don't know what this is, I just convert it 🤷‍♂️

**pitch: *float***  
Pitch offset of the panorama in radians, converted from OPK.

**provider: *str***  
The name of the company which created the panorama.

**roll: *float***  
Roll offset of the panorama in radians, converted from OPK.

**tile_size: *Size***  
Mapy panoramas are broken up into multiple tiles. This returns the size of one tile.

**uri_path: *str***  
Part of the panorama tile URL.


## Finding panoramas

#### <code>find_panorama(<em>lat: float, lon: float, radius: float = 100.0</em>) -> MapyPanorama | None</code>
Searches for a panorama within a radius around a point.

**lat**, **lon**: Latitude and longitude.  
**radius**: Search radius in meters.  

#### <code>get_neighbors(<em>panoid: int</em>) -> list[MapyPanorama]</code>
Gets neighbors of a panorama.

**panoid**: ID of the panorama.


## Downloading panoramas

#### <code>download_panorama(<em>pano: MapyPanorama, path: str, zoom: int = 2, pil_args: dict = None</em>) -> None</code>
Downloads a panorama to a file.

**pano**: The panorama.  
**path**: Output path.  
**zoom**: Image size; 0 is lowest, 2 is highest. If 2 is not available, 1 will be downloaded.  
**pil_args**: Additional arguments for the [`Image.save()`](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save) method, e.g. `pil_args={"quality":100}`.

#### <code>get_panorama(<em>pano: MapyPanorama, zoom: int = 2</em>) -> Image</code>
Like `download_panorama()`, but the panorama is returned as a PIL image.
