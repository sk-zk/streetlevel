import itertools
import math
from io import BytesIO
from typing import Union, List

import requests
from PIL import Image
from aiohttp import ClientSession

from .panorama import MapyPanorama
from . import api
from requests import Session
from ..dataclasses import Size
from ..geo import opk_to_rotation
from ..util import download_tiles, download_tiles_async, stitch_tiles


def find_panorama(lat: float, lon: float,
                  radius: float = 100.0) -> Union[MapyPanorama, None]:
    """
    Searches for a panorama within a radius around a point.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param radius: *(optional)* Search radius in meters. Defaults to 100.
    :return: A MapyPanorama object if a panorama was found, or None.
    """
    radius = float(radius)
    response = api.getbest(lat, lon, radius)

    if response["status"] != 200:
        return None

    pan_info = response["result"]["panInfo"]
    pano = _parse_pan_info_dict(pan_info)

    pano.neighbors = get_neighbors(pano.id)

    for year in pan_info["timeline"]:
        if pano.date.year == year:
            continue
        response = api.getbest(lat, lon, 50.0, options={'year': year, 'nopenalties': True})
        if response["status"] != 200:
            continue
        pan_info = response["result"]["panInfo"]
        historical = _parse_pan_info_dict(pan_info)
        pano.historical.append(historical)

    return pano


async def find_panorama_async(lat: float, lon: float,
                              radius: float = 100.0) -> Union[MapyPanorama, None]:
    # TODO reduce duplication
    radius = float(radius)
    response = await api.getbest_async(lat, lon, radius)

    if response["status"] != 200:
        return None

    pan_info = response["result"]["panInfo"]
    pano = _parse_pan_info_dict(pan_info)

    pano.neighbors = await get_neighbors_async(pano.id)

    for year in pan_info["timeline"]:
        if pano.date.year == year:
            continue
        response = await api.getbest_async(lat, lon, 50.0, options={'year': year, 'nopenalties': True})
        if response["status"] != 200:
            continue
        pan_info = response["result"]["panInfo"]
        historical = _parse_pan_info_dict(pan_info)
        pano.historical.append(historical)

    return pano


def get_neighbors(panoid: int) -> List[MapyPanorama]:
    """
    Gets neighbors of a panorama. (:func:`find_panorama` calls this automatically.)

    :param panoid: The pano ID.
    :return: A list of nearby panoramas.
    """
    response = api.getneighbors(panoid)

    if response["status"] != 200:
        return []

    return _getneighbors_response_to_list(response)


async def get_neighbors_async(panoid: int) -> List[MapyPanorama]:
    response = await api.getneighbors_async(panoid)

    if response["status"] != 200:
        return []

    return _getneighbors_response_to_list(response)


def get_panorama(pano: MapyPanorama, zoom: int = 2) -> Image.Image:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. If 2 is not available, 1 will be downloaded.
    :return: A PIL image containing the panorama.
    """
    zoom = max(0, min(zoom, pano.max_zoom))

    if zoom == 0:
        return _get_zoom_0(pano)
    else:
        tiles = _generate_tile_list(pano, zoom)
        tile_images = download_tiles(tiles)
        stitched = stitch_tiles(tile_images,
                                pano.tile_size.x * pano.num_tiles[zoom].x,
                                pano.tile_size.y * pano.num_tiles[zoom].y,
                                pano.tile_size.x,
                                pano.tile_size.y)
        return stitched


async def get_panorama_async(pano: MapyPanorama, session: ClientSession, zoom: int = 2) -> Image.Image:
    zoom = max(0, min(zoom, pano.max_zoom))

    if zoom == 0:
        return await _get_zoom_0_async(pano, session)
    else:
        tiles = _generate_tile_list(pano, zoom)
        tile_images = await download_tiles_async(tiles, session)
        stitched = stitch_tiles(tile_images,
                                pano.tile_size.x * pano.num_tiles[zoom].x,
                                pano.tile_size.y * pano.num_tiles[zoom].y,
                                pano.tile_size.x,
                                pano.tile_size.y)
        return stitched


def download_panorama(pano: MapyPanorama, path: str, zoom: int = 2, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.

    :param pano: The panorama.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. If 2 is not available, 1 will be downloaded.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}
    pano = get_panorama(pano, zoom=zoom)
    pano.save(path, **pil_args)


async def download_panorama_async(pano: MapyPanorama, path: str, session: ClientSession,
                                  zoom: int = 2, pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}
    pano = await get_panorama_async(pano, session, zoom=zoom)
    pano.save(path, **pil_args)


def _getneighbors_response_to_list(response):
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


def _get_zoom_0(pano: MapyPanorama, session: Session = None) -> Image.Image:
    tile_url = _generate_tile_list(pano, 0)[0][2]
    if session is None:
        session = requests.Session()
    response = session.get(tile_url)
    image = Image.open(BytesIO(response.content))
    return image


async def _get_zoom_0_async(pano: MapyPanorama, session: ClientSession) -> Image.Image:
    tile_url = _generate_tile_list(pano, 0)[0][2]
    response = await session.get(tile_url)
    image = Image.open(BytesIO(await response.read()))
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
