import asyncio
import itertools
import math
from io import BytesIO
import requests
from PIL import Image
from pyfrpc.client import FrpcClient
from .panorama import MapyPanorama
from requests import Session
from ..dataclasses import Size
from ..geo import opk_to_rotation
from ..util import download_files_async

client = FrpcClient("https://pro.mapy.cz/panorpc")
headers = {
    # Cyclomedia panos (2020+) are only returned if this header is set
    "Referer": "https://en.mapy.cz/",
}


def find_panorama(lat: float, lon: float,
                  radius: float = 100.0) -> MapyPanorama | None:
    response = _rpc_getbest(lat, lon, radius)

    if response["status"] != 200:
        return None

    pan_info = response["result"]["panInfo"]
    pano = _parse_pan_info_dict(pan_info)

    pano.neighbors = get_neighbors(pano.id)

    for year in pan_info["timeline"]:
        if pano.date.year == year:
            continue
        response = _rpc_getbest(lat, lon, 50.0, options={'year': year, 'nopenalties': True})
        if response["status"] != 200:
            continue
        pan_info = response["result"]["panInfo"]
        historical = _parse_pan_info_dict(pan_info)
        pano.historical.append(historical)

    return pano


def _rpc_getbest(lat, lon, radius, options=None):
    if options is None:
        options = {}
    response = client.call("getbest",
                           args=(lon, lat, radius, options),
                           headers=headers)
    return response


def get_neighbors(panoid: int) -> list[MapyPanorama]:
    response = client.call("getneighbours",
                           args=(panoid,),
                           headers=headers)

    if response["status"] != 200:
        return []

    panos = []
    for pan_info in response["result"]["neighbours"]:
        panos.append(_parse_pan_info_dict(pan_info["near"]))
    return panos


def _parse_pan_info_dict(pan_info: dict) -> MapyPanorama:
    pano = MapyPanorama(
        id=pan_info["pid"],
        lat=pan_info["mark"]["lat"],
        lon=pan_info["mark"]["lon"],
        tile_size=Size(pan_info["tileWidth"], pan_info["tileHeight"]),
        domain_prefix=pan_info["domainPrefix"],
        uri_path=pan_info["uriPath"],
        file_mask=pan_info["fileMask"],
        max_zoom=pan_info["maxZoom"],
        date=pan_info["createdAt"],
        elevation=pan_info["mark"]["alt"],
        provider=pan_info["provider"],
    )

    _parse_angles(pan_info, pano)
    _parse_num_tiles(pan_info, pano)

    return pano


def _parse_num_tiles(pan_info, pano):
    # zoom level 0
    num_tiles = [Size(1, 1)]
    # zoom levels 1 and 2 for cyclomedia
    if "extra" in pan_info and "tileNumX" in pan_info["extra"]:
        for i in range(0, len(pan_info["extra"]["tileNumX"])):
            num = Size(int(pan_info["extra"]["tileNumX"][i]),
                       int(pan_info["extra"]["tileNumY"][i]))
            num_tiles.append(num)
    # zoom level 1 for other providers
    else:
        num_tiles.append(Size(pan_info["tileNumX"], pan_info["tileNumY"]))
    pano.num_tiles = num_tiles


def _parse_angles(pan_info, pano):
    if "extra" in pan_info and "carDirection" in pan_info["extra"]:
        pano.heading = math.radians(pan_info["extra"]["carDirection"])

    pano.omega = math.radians(pan_info["omega"])
    pano.phi = math.radians(pan_info["phi"])
    pano.kappa = math.radians(pan_info["kappa"])
    heading, pitch, roll = opk_to_rotation(pano.omega, pano.phi, pano.kappa).as_euler('yxz')
    if not pano.heading:
        pano.heading = heading
    pano.pitch = pitch
    pano.roll = roll


def get_panorama(pano: MapyPanorama, zoom: int = 2) -> Image:
    """
    Downloads a panorama as PIL image.
    """
    zoom = max(0, min(zoom, pano.max_zoom))

    if zoom == 0:
        return _get_zoom_0(pano)
    else:
        tiles = _generate_tile_list(pano, zoom)
        tile_images = _download_tiles(tiles)
        stitched = _stitch_tiles(pano, tiles, tile_images, zoom)
        return stitched


def download_panorama(pano: MapyPanorama, path: str, zoom: int = 2, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.
    """
    if pil_args is None:
        pil_args = {}
    pano = get_panorama(pano, zoom=zoom)
    pano.save(path, **pil_args)


def _get_zoom_0(pano: MapyPanorama, session: Session = None) -> Image:
    tile_url = _generate_tile_list(pano, 0)[0][2]
    if session is None:
        session = requests.Session()
    response = session.get(tile_url)
    image = Image.open(BytesIO(response.content))
    return image


def _generate_tile_list(pano: MapyPanorama, zoom: int):
    """
    Generates a list of a panorama's tiles.
    Returns a list of (x, y, tile_url) tuples.
    """
    file_mask = pano.file_mask
    file_mask = file_mask.replace("xx", "{0:02x}") \
        .replace("yy", "{1:02x}") \
        .replace("zz", "{2:02x}")
    url = f"https://panorama-mapserver.mapy.cz/panorama/" \
          f"{pano.domain_prefix}/{pano.uri_path}/{file_mask}"

    coords = list(itertools.product(range(pano.num_tiles[zoom].x), range(pano.num_tiles[zoom].y)))
    tiles = [(x, y, url.format(x, y, zoom)) for x, y in coords]
    return tiles


def _download_tiles(tile_list):
    """
    Downloads tiles from a tile list generated by _generate_tile_list().
    """
    tiles = asyncio.run(download_files_async([t[2] for t in tile_list]))

    tile_images = {}
    for i, (x, y, url) in enumerate(tile_list):
        tile_images[(x, y)] = tiles[i]

    return tile_images


def _stitch_tiles(pano: MapyPanorama, tile_list, tile_images, zoom: int) -> Image:
    """
    Stitches downloaded tiles to a full image.
    """
    img_width = pano.tile_size.x * pano.num_tiles[zoom].x
    img_height = pano.tile_size.y * pano.num_tiles[zoom].y
    tile_width = pano.tile_size.x
    tile_height = pano.tile_size.y

    stitched = Image.new('RGB', (img_width, img_height))

    for x, y, url in tile_list:
        tile = Image.open(BytesIO(tile_images[(x, y)]))
        stitched.paste(im=tile, box=(x * tile_width, y * tile_height))
        del tile

    return stitched
