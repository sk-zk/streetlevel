import itertools
import math
from typing import List, Optional
from datetime import datetime

import requests
from PIL import Image
from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import KakaoPanorama, PanoramaType
from ..dataclasses import Tile, Size, Link
from ..util import try_get, get_equirectangular_panorama, get_equirectangular_panorama_async, get_image, \
    get_image_async, download_file, download_file_async

PANO_COLS = [1, 8, 16]
PANO_ROWS = [1, 4, 8]
PANO_TILE_SIZE = Size(512, 512)
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
    response = api.find_panoramas(lat, lon, radius, limit, session)

    if response["street_view"]["cnt"] == 0:
        return []

    return _parse_panoramas(response)


async def find_panoramas_async(lat: float, lon: float, session: ClientSession,
                               radius: int = 35, limit: int = 50) -> List[KakaoPanorama]:
    response = await api.find_panoramas_async(lat, lon, session, radius, limit)

    if response["street_view"]["cnt"] == 0:
        return []

    return _parse_panoramas(response)


def find_panorama_by_id(panoid: int, neighbors: bool = True, session: Session = None) -> Optional[KakaoPanorama]:
    """
    Fetches metadata of a specific panorama.

    This call only appears to work for the most recent coverage at a location. IDs of older panoramas will return
    nothing even though they exist.

    :param panoid: The pano ID.
    :param neighbors: *(optional)* Whether an additional network request is made to fetch nearby panoramas.
        Defaults to True.
    :param session: *(optional)* A requests session.
    :return: A KakaoPanorama object if a panorama with this ID was found, or None.
    """
    response = api.find_panorama_by_id(panoid, session)

    if response["street_view"]["cnt"] == 0:
        return None

    pano = _parse_panorama(response["street_view"]["street"])
    if neighbors:
        pano.neighbors = find_panoramas(pano.lat, pano.lon, session=session)
    return pano


async def find_panorama_by_id_async(panoid: int, session: ClientSession,
                                    neighbors: bool = True) -> Optional[KakaoPanorama]:
    response = await api.find_panorama_by_id_async(panoid, session)

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

    zoom = _validate_zoom(pano, zoom)
    return get_equirectangular_panorama(
        PANO_COLS[zoom] * PANO_TILE_SIZE.x,
        PANO_ROWS[zoom] * PANO_TILE_SIZE.y,
        PANO_TILE_SIZE,
        _generate_tile_list(pano, zoom))


async def get_panorama_async(pano: KakaoPanorama, session: ClientSession, zoom: int = 2) -> Image.Image:
    if zoom == 0:
        return await _get_thumbnail_async(pano, session)

    zoom = await _validate_zoom_async(pano, zoom, session)
    return await get_equirectangular_panorama_async(
        PANO_COLS[zoom] * PANO_TILE_SIZE.x,
        PANO_ROWS[zoom] * PANO_TILE_SIZE.y,
        PANO_TILE_SIZE,
        _generate_tile_list(pano, zoom),
        session)


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


def get_depthmap(pano: KakaoPanorama, session: Session = None) -> Image.Image:
    """
    Downloads the depth map of a panorama and returns it as PIL image.

    :param pano: The panorama.
    :param session: *(optional)* A requests session.
    :return: The depth map as PIL Image.
    """
    return get_image(_build_depthmap_url(pano), session=session)


async def get_depthmap_async(pano: KakaoPanorama, session: ClientSession) -> Image.Image:
    return await get_image_async(_build_depthmap_url(pano), session)


def download_depthmap(pano: KakaoPanorama, path: str, session: Session = None) -> None:
    """
    Downloads the depth map of a panorama to a PNG file.

    :param pano: The panorama.
    :param path: Output path.
    :param session: *(optional)* A requests session.
    """
    download_file(_build_depthmap_url(pano), path, session=session)


async def download_depthmap_async(pano: KakaoPanorama, path: str, session: ClientSession) -> None:
    await download_file_async(_build_depthmap_url(pano), path, session)


def _build_depthmap_url(pano):
    return f"https://map.daumcdn.net/map_roadview/depthmap_meerkat" \
           f"{pano.image_path}_W.png"


def _parse_panoramas(response):
    return [_parse_panorama(pano) for pano in response["street_view"]["streetList"]]


def _parse_panorama(pano_json: dict) -> KakaoPanorama:
    pano = KakaoPanorama(
        id=pano_json["id"],
        lat=pano_json["wgsy"],
        lon=pano_json["wgsx"],
        wcongx=pano_json["wcongx"],
        wcongy=pano_json["wcongy"],
        heading=math.radians(float(pano_json["angle"])),
        image_path=pano_json["img_path"],
        # shot_date sometimes returns the time as 00:00:00, but the image url is always correct
        date=datetime.strptime(pano_json["img_path"].split("_")[-1], "%Y%m%d%H%M%S"),
        street_name=try_get(lambda: pano_json["st_name"]),
        address=try_get(lambda: pano_json["addr"]),
        street_type=try_get(lambda: pano_json["st_type"]),
        panorama_type=PanoramaType(int(pano_json["shot_tool"]))
    )

    if "past" in pano_json and pano_json["past"] is not None:
        pano.historical = [_parse_panorama(past) for past in pano_json["past"]]

    if "spot" in pano_json and pano_json["past"] is not None:
        pano.links = _parse_links(pano_json["spot"])

    return pano


def _parse_links(links_json: List[dict]) -> List[Link]:
    links = []
    for linked_json in links_json:
        linked = KakaoPanorama(
            id=linked_json["id"],
            lat=linked_json["wgsy"],
            lon=linked_json["wgsx"],
            street_name=try_get(lambda: linked_json["st_name"]),
        )
        angle = math.radians(float(linked_json["pan"]))
        links.append(Link(linked, angle))
    return links


def _generate_tile_list(pano: KakaoPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    if not (zoom == 1 or zoom == 2):
        raise ValueError("Call _get_thumbnail")

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
    return get_image(PANO_TILE_URL_TEMPLATE[0].format(pano.image_path), session=session)


async def _get_thumbnail_async(pano: KakaoPanorama, session: ClientSession) -> Image.Image:
    return await get_image_async(PANO_TILE_URL_TEMPLATE[0].format(pano.image_path), session)


def _validate_zoom(pano, zoom):
    zoom = max(0, min(2, zoom))
    if zoom == 0:
        raise ValueError("Call _get_thumbnail")
    elif zoom == 2:
        # some panoramas don't have a high resolution version, but the metadata does not
        # indicate whether this is the case, so it seems the only way to know whether
        # it exists or not is to HEAD a tile and hope we get a 200. otherwise, fall back to 1.
        url = _build_tile_url(2, pano.image_path, 0, 0)
        response = requests.head(url)
        if response.status_code != 200:
            zoom = 1
    return zoom


async def _validate_zoom_async(pano, zoom, session):
    zoom = max(0, min(2, zoom))
    if zoom == 0:
        raise ValueError("Call _get_thumbnail")
    elif zoom == 2:
        url = _build_tile_url(zoom, pano.image_path, 0, 0)
        response = await session.head(url)
        if response.status != 200:
            zoom = 1
    return zoom
