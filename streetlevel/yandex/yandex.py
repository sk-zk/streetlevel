import itertools
import math
from typing import List, Optional

from PIL import Image
from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import YandexPanorama
from .parse import parse_panorama_response
from ..dataclasses import Tile
from ..exif import save_with_metadata, OutputMetadata
from ..util import get_equirectangular_panorama, get_equirectangular_panorama_async


def find_panorama(lat: float, lon: float, session: Session = None) -> Optional[YandexPanorama]:
    """
    Searches for a panorama near the given point.

    Aerial panoramas are ignored by this API call.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param session: *(optional)* A requests session.
    :return: A YandexPanorama object if a panorama was found, or None.
    """

    response = api.find_panorama(lat, lon, session)
    return parse_panorama_response(response)


async def find_panorama_async(lat: float, lon: float, session: ClientSession) -> Optional[YandexPanorama]:
    response = await api.find_panorama_async(lat, lon, session)
    return parse_panorama_response(response)


def find_panorama_by_id(panoid: str, session: Session = None) -> Optional[YandexPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: A YandexPanorama object if a panorama with this ID exists, or None.
    """
    response = api.find_panorama_by_id(panoid, session)
    return parse_panorama_response(response)


async def find_panorama_by_id_async(panoid: str, session: ClientSession) -> Optional[YandexPanorama]:
    response = await api.find_panorama_by_id_async(panoid, session)
    return parse_panorama_response(response)


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
    Downloads a panorama to a file. If the chosen format is JPEG, Exif and XMP GPano metadata are included.

    Note that most official car coverage has its bottom part cropped out.

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
    save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))


async def download_panorama_async(pano: YandexPanorama, path: str, session: ClientSession,
                                  zoom: int = 0, pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}
    image = await get_panorama_async(pano, session, zoom=zoom)
    save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))


def _build_output_metadata_object(pano: YandexPanorama, image: Image.Image) -> OutputMetadata:
    if pano.heading:
        heading = math.pi / 2 - pano.heading + math.pi / 2
    else:
        heading = None
    return OutputMetadata(
        width=image.width,
        height=image.height,
        panoid=pano.id,
        lat=pano.lat,
        lon=pano.lon,
        creator=pano.author if pano.author else "Yandex",
        is_equirectangular=True,
        date=pano.date,
        heading=heading,
    )


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
