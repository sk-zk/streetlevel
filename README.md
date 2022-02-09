**streetlevel** is a module for downloading panoramas and metadata from Google StreetView and Bing Streetside.

Since it relies on internal / inofficial API calls, it may break unexpectedly.

## Example

Downloading the closest StreetView panorama to specific location:

```
from streetlevel import streetview

panos = streetview.find_panoramas(66.6804141, 34.3093958)
streetview.download_panorama(panos[0], ".")
```

## Documentation

Documentation of all available functionality is available in the `doc` folder.