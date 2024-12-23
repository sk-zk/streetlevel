# streetlevel
**streetlevel** is a library for downloading panoramas and metadata from street-level imagery services
such as Google Street View, Apple Look Around, and several others. It provides a simple abstraction
over the internal APIs of the supported services &ndash; this means that no API keys are required, but the
library may break unexpectedly. 

(Nearly) all functions are available as either a sync function using `requests` or an async function
using `aiohttp`, requiring a `ClientSession`.

## Installation
```sh
pip install streetlevel
```

## Example
Downloading the closest Google Street View panorama to a specific location, sync:

```python
from streetlevel import streetview

pano = streetview.find_panorama(46.883958, 12.169002)
streetview.download_panorama(pano, f"{pano.id}.jpg")
```

Or async:

```python
from streetlevel import streetview
from aiohttp import ClientSession

async with ClientSession() as session:
    pano = await streetview.find_panorama_async(46.883958, 12.169002, session)
    await streetview.download_panorama_async(pano, f"{pano.id}.jpg", session)
```

## Documentation
Documentation is available at [streetlevel.readthedocs.io](https://streetlevel.readthedocs.io/).

## Functionality overview
Services covering multiple countries are on the left; services covering one specific country are on the right.

✔ implemented / available; 🟡 partially implemented; ❌ not implemented; ⚫ not available / not applicable

<table>
  <thead>
    <th></th>
    <th align="center">Google<br>Street&nbsp;View</th>
    <th align="center">Apple<br>Look&nbsp;Around</th>
    <th align="center">Yandex<br>Panorama</th>
    <th align="center">Bing<br>Streetside</th>
    <th></th>
    <th align="center">🇨🇳 Baidu<br>Panorama</th>
    <th align="center">🇰🇷 Kakao<br>Road&nbsp;View</th>
    <th align="center">🇰🇷 Naver<br>Street&nbsp;View</th>
    <th align="center">🇨🇿 Mapy.cz<br>Panorama</th>
    <th align="center">🇮🇸 Já<br>360</th>
  </thead>
  <thead>
    <td colspan="11" style="padding-top:20px"><br><b>Finding panoramas</b><br>
      How panoramas can be retrieved through the API.
    </td>
  </thead>
  <tr>
    <td align="right">Find panoramas around a point</td>
    <td align="center">✔<sup>1</sup></td>
    <td align="center">⚫</td>
    <td align="center">✔<sup>1</sup></td>
    <td align="center">✔</td>
    <td></td>
    <td align="center">✔<sup>1</sup></td>
    <td align="center">✔</td>
    <td align="center">✔<sup>1</sup></td>
    <td align="center">✔<sup>1</sup></td>
    <td align="center">✔<sup>1</sup></td>
  </tr>
  <tr>
    <td align="right">Find panoramas by map tile or bbox</td>
    <td align="center">✔<sup>2</sup></td>
    <td align="center">✔<sup>2</sup></td>
    <td align="center">⚫</td>
    <td align="center">✔<sup>3</sup></td>
    <td></td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
  </tr>
  <tr>
    <td align="right">Get specific panorama by ID</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
  </tr>
  <thead>
    <td colspan="11" style="padding-top:20px"><br><b>Imagery</b><br>
      The type of imagery returned by the service.
    </td>
  </thead>
  <tr>
    <td align="right">Panoramas</td>
    <td align="center">✔</td>
    <td align="center">✔<sup>4</sup></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
  </tr>
  <tr>
    <td align="right">Depth</td>
    <td align="center">✔<sup>5</sup></td>
    <td align="center">❌</td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
    <td></td>
    <td align="center">❌?<sup>10</sup></td>
    <td align="center">✔</td>
    <td align="center">✔<sup>14</sup></td>
    <td align="center">⚫<br></td>
    <td align="center">⚫<br></td>
  </tr>
  <tr>
    <td align="right">Image projection</td>
    <td align="center">Equirectangular</td>
    <td align="center">???</td>
    <td align="center">Equirectangular</td>
    <td align="center">Cubemap</td>
    <td></td>
    <td align="center">Equirectangular</td>
    <td align="center">Equirectangular</td>
    <td align="center">Equirectangular/Cubemap<sup>13</sup></td>
    <td align="center">Equirectangular</td>
    <td align="center">Cubemap</td>
  </tr>
  <tr>
    <td align="right">Image format</td>
    <td align="center">JPEG</td>
    <td align="center">HEIC</td>
    <td align="center">JPEG</td>
    <td align="center">JPEG</td>
    <td></td>
    <td align="center">JPEG</td>
    <td align="center">JPEG</td>
    <td align="center">JPEG</td>
    <td align="center">JPEG</td>
    <td align="center">JPEG</td>
  </tr>
  <thead>
    <td colspan="11" style="padding-top:20px"><br><b>Available metadata</b><br>
      Metadata returned by the API of the service alongside ID and location.
    </td>
  </thead>
  <tr>
    <td align="right">Capture date</td>
    <td align="center">✔<sup>6</sup></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔<sup>9</sup></td>
  </tr>
  <tr>
    <td align="right">Heading, pitch, roll</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔<sup>7</sup></td>
    <td align="center">✔</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">✔<sup>7</sup></td>
    <td align="center">✔<sup>11</sup></td>
    <td align="center">✔</td>
    <td align="center">✔<sup>7</sup></td>
  </tr>
  <tr>
    <td align="right">Elevation</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">⚫<sup>12</sup></td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
  </tr>
  <tr>
    <td align="right">Nearby / linked panoramas</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">✔<sup>8</sup></td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
  </tr>
  <tr>
    <td align="right">Historical panoramas</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
  </tr>
  <tr>
    <td align="right">Address</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td></td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
  </tr>
  <tr>
    <td align="right">PoIs</td>
    <td align="center">✔</td>
    <td align="center">❌</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td></td>
    <td align="center">⚫</td>
    <td align="center">❌</td>
    <td align="center">❌</td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
  </tr>
  <tr>
    <td align="right">Creator</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td></td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
    <td align="center">⚫</td>
    <td align="center">✔</td>
    <td align="center">⚫</td>
  </tr>
</table>

1: Returns closest only  
2: Tile, z=17  
3: Bounding box  
4: Unstitched  
5: Appears to be a synthetic depth map created from elevation data and building footprints  
6: Month and year only for official coverage, full date for inofficial coverage  
7: Only heading; pitch/roll do not appear to be available  
8: Previous and next image in sequence  
9: Month and year only  
10: There is a `has_depth` field in the raw metadata, but I've yet to find a panorama that actually has depth  
11: Pitch/roll are only available for the new 3D imagery  
12: Camera altitude is available, however  
13: 3D imagery panos have both an equirectangular and a cubemap version; everything else is only available as cubemap  
14: Non-3D imagery appears to use a synthetic depthmap created from elevation data and building footprints
