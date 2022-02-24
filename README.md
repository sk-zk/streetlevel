**streetlevel** is a module for downloading panoramas and metadata from Google StreetView and Bing Streetside.

Since it relies on internal / inofficial API calls, it may break unexpectedly.

## Example

Downloading the closest StreetView panorama to specific location:

```
from streetlevel import streetview

panos = streetview.find_panoramas(46.8839586, 12.169002)
streetview.download_panorama(panos[0], f"{panos[0].id}.jpg")
```

## Documentation

Documentation of all available functionality can be found in the `doc` folder.