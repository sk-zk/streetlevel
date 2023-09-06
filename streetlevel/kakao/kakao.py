import itertools
import math
from io import BytesIO
from typing import List, Optional
from datetime import datetime

import requests
from PIL import Image
from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import KakaoPanorama, CameraType
from ..dataclasses import Tile
from ..util import try_get, download_tiles, stitch_tiles, download_tiles_async

PANO_COLS = [1, 8, 16]
PANO_ROWS = [1, 4, 8]
PANO_TILE_SIZE = 512
PANO_TILE_URL_TEMPLATE = [
    "https://map.daumcdn.net/map_roadview{0}.jpg",
    "https://map.daumcdn.net/map_roadview{0}/{1}_{2:02d}.jpg",
    "https://map.daumcdn.net/map_roadview{0}_HD1/{1}_HD1_{2:03d}.jpg"
    ]


def find_panoramas(lat: float, lon: float, radius: int = 35,
                   limit: int = 50, session: Session = None) -> List[KakaoPanorama]:
    """
    Searches for panoramas within a radius around a point.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param radius: *(optional)* Search radius in meters, max. 100. Defaults to 35, which is the value used by
        the KakaoMap client when fetching neighboring panoramas.
    :param limit: *(optional)* Number of results to return, max. 100. Defaults to 50, which is the value used by
        the KakaoMap client when fetching neighboring panoramas.
    :param session: *(optional)* A requests session.
    :return: A list of KakaoPanorama objects.
    """
    response = api.find_panoramas_raw(lat, lon, radius, limit, session)

    if response["street_view"]["cnt"] == 0:
        return []

    return _parse_panoramas(response)


async def find_panoramas_async(lat: float, lon: float, session: ClientSession,
                               radius: int = 35, limit: int = 50) -> List[KakaoPanorama]:
    response = await api.find_panoramas_raw_async(lat, lon, session, radius, limit)

    if response["street_view"]["cnt"] == 0:
        return []

    return _parse_panoramas(response)


def find_panorama_by_id(panoid: int, neighbors: bool = True, session: Session = None) -> Optional[KakaoPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The pano ID.
    :param neighbors: *(optional)* Whether an additional network request is made to fetch nearby panoramas.
        Defaults to True.
    :param session: *(optional)* A requests session.
    :return: A KakaoPanorama object if a panorama with this ID exists, or None.
    """
    response = api.find_panorama_by_id_raw(panoid, session)

    if response["street_view"]["cnt"] == 0:
        return None

    pano = _parse_panorama(response["street_view"]["street"])
    if neighbors:
        pano.neighbors = find_panoramas(pano.lat, pano.lon, session=session)
    return pano


async def find_panorama_by_id_async(panoid: int, session: ClientSession, neighbors: bool = True) -> Optional[KakaoPanorama]:
    response = await api.find_panorama_by_id_raw_async(panoid, session)

    if response["street_view"]["cnt"] == 0:
        return None

    pano = _parse_panorama(response["street_view"]["street"])
    if neighbors:
        pano.neighbors = await find_panoramas_async(pano.lat, pano.lon, session)
    return pano


def get_panorama(pano: KakaoPanorama, zoom: int = 2) -> Image.Image:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama to download.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. Defaults to 2.
        If 2 is unavailable, 1 will be downloaded.
    :return: A PIL image containing the panorama.
    """
    if zoom == 0:
        return _get_thumbnail(pano)

    # some panoramas don't have a high resolution version, but the metadata does not
    # indicate whether this is the case, so it seems the only way to know whether
    # it exists or not is to HEAD a tile and hope we get a 200. otherwise, fall back to 1.
    if zoom == 2 and not _zoom_2_exists(pano):
        zoom = 1

    tile_list = _generate_tile_list(pano, zoom)

    tile_images = download_tiles(tile_list)
    stitched = stitch_tiles(tile_images,
                            PANO_COLS[zoom] * PANO_TILE_SIZE, PANO_ROWS[zoom] * PANO_TILE_SIZE,
                            PANO_TILE_SIZE, PANO_TILE_SIZE)
    return stitched


async def get_panorama_async(pano: KakaoPanorama, session: ClientSession, zoom: int = 2) -> Image.Image:
    if zoom == 0:
        return await _get_thumbnail_async(pano, session)

    if zoom == 2 and not (await _zoom_2_exists_async(pano, session)):
        zoom = 1

    tile_list = _generate_tile_list(pano, zoom)
    tile_images = await download_tiles_async(tile_list, session)
    stitched = stitch_tiles(tile_images,
                            PANO_COLS[zoom] * PANO_TILE_SIZE, PANO_ROWS[zoom] * PANO_TILE_SIZE,
                            PANO_TILE_SIZE, PANO_TILE_SIZE)
    return stitched


def download_panorama(pano: KakaoPanorama, path: str, zoom: int = 2, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.

    :param pano: The panorama to download.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. Defaults to 2.
        If 2 is unavailable, 1 will be downloaded.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}
    image = get_panorama(pano, zoom=zoom)
    image.save(path, **pil_args)


async def download_panorama_async(pano: KakaoPanorama, path: str, session: ClientSession,
                                  zoom: int = 2, pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}
    image = await get_panorama_async(pano, session, zoom=zoom)
    image.save(path, **pil_args)


def _parse_panoramas(response):
    return [_parse_panorama(pano) for pano in response["street_view"]["streetList"]]


def _parse_panorama(pano_json: dict) -> KakaoPanorama:
    pano = KakaoPanorama(
        id=pano_json["id"],
        lat=pano_json["wgsy"],
        lon=pano_json["wgsx"],
        heading=math.radians(float(pano_json["angle"])),
        image_path=pano_json["img_path"],
        # shot_date sometimes returns the time as 00:00:00, but the image url is always correct
        date=datetime.strptime(pano_json["img_path"].split("_")[-1], "%Y%m%d%H%M%S"),
        street_name=try_get(lambda: pano_json["st_name"]),
        address=try_get(lambda: pano_json["addr"]),
        street_type=try_get(lambda: pano_json["st_type"]),
        camera_type=CameraType(int(pano_json["shot_tool"]))
    )
    if "past" in pano_json and pano_json["past"] is not None:
        pano.historical = [_parse_panorama(past) for past in pano_json["past"]]
    return pano


def _generate_tile_list(pano: KakaoPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    if not (zoom == 1 or zoom == 2):
        raise ValueError()

    coords = list(itertools.product(range(PANO_COLS[zoom]), range(PANO_ROWS[zoom])))
    tiles = [Tile(x, y, _build_tile_url(zoom, pano.image_path, x, y)) for x, y in coords]
    return tiles


def _build_tile_url(zoom: int, image_path: str, x: int, y: int) -> str:
    return PANO_TILE_URL_TEMPLATE[zoom].format(
        image_path,
        image_path.split("/")[-1],
        (y * PANO_COLS[zoom]) + x + 1
    )


def _get_thumbnail(pano: KakaoPanorama, session: Session = None) -> Image.Image:
    tile_url = PANO_TILE_URL_TEMPLATE[0].format(pano.image_path)
    requester = session if session else requests
    response = requester.get(tile_url)
    image = Image.open(BytesIO(response.content))
    return image


async def _get_thumbnail_async(pano: KakaoPanorama, session: ClientSession) -> Image.Image:
    tile_url = PANO_TILE_URL_TEMPLATE[0].format(pano.image_path)
    response = await session.get(tile_url)
    image = Image.open(BytesIO(await response.read()))
    return image


def _zoom_2_exists(pano: KakaoPanorama) -> bool:
    url = _build_tile_url(2, pano.image_path, 0, 0)
    response = requests.head(url)
    return response.status_code == 200


async def _zoom_2_exists_async(pano: KakaoPanorama, session: ClientSession) -> bool:
    url = _build_tile_url(2, pano.image_path, 0, 0)
    response = await session.head(url)
    return response.status == 200
