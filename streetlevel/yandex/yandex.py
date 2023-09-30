import itertools
import math
from datetime import datetime
from typing import List, Optional
import re

from PIL import Image
from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import YandexPanorama
from ..dataclasses import Size, Tile, Link
from ..util import try_get, get_equirectangular_panorama, get_equirectangular_panorama_async


def find_panorama(lat: float, lon: float, session: Session = None) -> Optional[YandexPanorama]:
    """
    Searches for a panorama near the given point.

    Aerial panoramas are ignored by this API call.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param session: *(optional)* A requests session.
    :return: A YandexPanorama object if a panorama was found, or None.
    """

    resp = api.find_panorama_raw(lat, lon, session)

    if resp["status"] == "error":
        return None

    pano = _parse_panorama(resp["data"])
    return pano


async def find_panorama_async(lat: float, lon: float, session: ClientSession) -> Optional[YandexPanorama]:
    resp = await api.find_panorama_raw_async(lat, lon, session)

    if resp["status"] == "error":
        return None

    pano = _parse_panorama(resp["data"])
    return pano


def find_panorama_by_id(panoid: str, session: Session = None) -> Optional[YandexPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: A YandexPanorama object if a panorama with this ID exists, or None.
    """
    resp = api.find_panorama_by_id_raw(panoid, session)

    if resp["status"] == "error":
        return None

    pano = _parse_panorama(resp["data"])
    return pano


async def find_panorama_by_id_async(panoid: str, session: ClientSession) -> Optional[YandexPanorama]:
    resp = await api.find_panorama_by_id_raw_async(panoid, session)

    if resp["status"] == "error":
        return None

    pano = _parse_panorama(resp["data"])
    return pano


def get_panorama(pano: YandexPanorama, zoom: int = 0) -> Image.Image:
    """
    Downloads a panorama and returns it as PIL image.

    Note that most official car coverage has its bottom part cropped out.

    :param pano: The panorama to download.
    :param zoom: *(optional)* Image size; 0 is highest, 4 is lowest. The dimensions of a zoom level of a
        specific panorama depend on the camera used. If the requested zoom level does not exist,
        the highest available level will be downloaded. Defaults to 0.
    :return: A PIL image containing the panorama.
    """
    zoom = _validate_get_panorama_params(pano, zoom)
    return get_equirectangular_panorama(
        pano.image_sizes[zoom].x, pano.image_sizes[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom))


async def get_panorama_async(pano: YandexPanorama, session: ClientSession, zoom: int = 0) -> Image.Image:
    zoom = _validate_get_panorama_params(pano, zoom)
    return await get_equirectangular_panorama_async(
        pano.image_sizes[zoom].x, pano.image_sizes[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom),
        session)


def download_panorama(pano: YandexPanorama, path: str, zoom: int = 0, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.

    :param pano: The panorama to download.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is highest, 4 is lowest. The dimensions of a zoom level of a
        specific panorama depend on the camera used. If the requested zoom level does not exist,
        the highest available level will be downloaded. Defaults to 0.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}
    image = get_panorama(pano, zoom=zoom)
    image.save(path, **pil_args)


async def download_panorama_async(pano: YandexPanorama, path: str, session: ClientSession,
                                  zoom: int = 0, pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}
    image = await get_panorama_async(pano, session, zoom=zoom)
    image.save(path, **pil_args)


def _generate_tile_list(pano: YandexPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    img_size = pano.image_sizes[zoom]
    tile_width = pano.tile_size.x
    tile_height = pano.tile_size.y
    cols = math.ceil(img_size.x / tile_width)
    rows = math.ceil(img_size.y / tile_height)

    IMAGE_URL = "https://pano.maps.yandex.net/{0:}/{1:}.{2:}.{3:}"

    coords = list(itertools.product(range(cols), range(rows)))
    tiles = [Tile(x, y, IMAGE_URL.format(pano.image_id, zoom, x, y)) for x, y in coords]
    return tiles


def _validate_get_panorama_params(pano: YandexPanorama, zoom: int) -> int:
    if not pano.image_sizes:
        raise ValueError("pano.image_sizes is None.")
    zoom = max(0, min(zoom, len(pano.image_sizes) - 1))
    return zoom


def _parse_panorama(data: dict) -> YandexPanorama:
    panoid = data["Data"]["panoramaId"]
    return YandexPanorama(
        id=panoid,
        lat=float(data["Data"]["Point"]["coordinates"][1]),
        lon=float(data["Data"]["Point"]["coordinates"][0]),

        heading=math.radians(float(data["Data"]["EquirectangularProjection"]["Origin"][0])),

        image_id=data["Data"]["Images"]["imageId"],
        tile_size=Size(int(data["Data"]["Images"]["Tiles"]["width"]),
                       int(data["Data"]["Images"]["Tiles"]["height"])),
        image_sizes=_parse_image_sizes(data["Data"]["Images"]["Zooms"]),

        neighbors=_parse_neighbors(data["Annotation"]["Graph"]["Nodes"], panoid),
        links=_parse_links(data["Annotation"]["Thoroughfares"]),
        historical=_parse_historical(data["Annotation"]["HistoricalPanoramas"], panoid),

        date=_get_date_from_panoid(panoid),
        height=int(data["Data"]["Point"]["coordinates"][2]),
        street_name=data["Data"]["Point"]["name"],

        author=try_get(lambda: data["Author"]["name"]),
        author_avatar_url=try_get(lambda: data["Author"]["avatarUrlTemplate"]),
    )


def _parse_links(links_json):
    links = []
    for link_json in links_json:
        panoid = re.findall(r"oid=(.*?)&", link_json["Connection"]["href"])[0]
        angle = math.radians(float(link_json["Direction"][0]))
        links.append(Link(panoid, angle))
    return links


def _get_date_from_panoid(panoid: str) -> datetime:
    return datetime.utcfromtimestamp(int(panoid.split("_")[-1]))


def _parse_image_sizes(zooms: dict) -> List[Size]:
    sizes = [None] * len(zooms)
    for zoom in zooms:
        idx = int(zoom["level"])
        sizes[idx] = Size(int(zoom["width"]), int(zoom["height"]))
    return sizes


def _parse_neighbors(nodes: List[dict], parent_id: str) -> List[YandexPanorama]:
    panos = []
    for node in nodes:
        panoid = node["panoid"]
        if panoid == parent_id:
            continue
        pano = YandexPanorama(
            id=panoid,
            lat=float(node["lat"]),
            lon=float(node["lon"]),
            date=_get_date_from_panoid(panoid)
        )
        panos.append(pano)
    return panos


def _parse_historical(historical: List[dict], parent_id: str) -> List[YandexPanorama]:
    panos = []
    for raw_pano in historical:
        panoid = raw_pano["Connection"]["oid"]
        if panoid == parent_id:
            continue
        pano = YandexPanorama(
            id=panoid,
            lat=float(raw_pano["Connection"]["Point"]["coordinates"][1]),
            lon=float(raw_pano["Connection"]["Point"]["coordinates"][0]),
            height=int(raw_pano["Connection"]["Point"]["coordinates"][2]),
            date=_get_date_from_panoid(panoid)
        )
        panos.append(pano)
    panos = sorted(panos, key=lambda x: x.date, reverse=True)
    return panos
