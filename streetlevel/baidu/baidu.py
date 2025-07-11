import itertools
import math
from enum import Enum
from typing import Optional, List, Tuple

from PIL import Image
from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import BaiduPanorama, InteriorMetadata
from .parse import parse_panorama_response, parse_inter_response
from ..dataclasses import Tile
from ..exif import save_with_metadata, OutputMetadata
from ..geo import wgs84_to_bd09mc, bd09_to_bd09mc, gcj02_to_bd09mc
from ..util import get_equirectangular_panorama, get_equirectangular_panorama_async


class Crs(Enum):
    """
    Coordinate systems supported by ``find_panorama``.
    """
    WGS84 = 0  #:
    BD09 = 1  #:
    BD09MC = 2  #:
    GCJ02 = 3  #:


def find_panorama(coord1: float, coord2: float, crs: Crs = Crs.WGS84, session: Session = None) \
        -> Optional[BaiduPanorama]:
    """
    Searches for a panorama near the given point.

    :param coord1: Latitude or x coordinate of the point.
    :param coord2: Longitude or y coordinate of the point.
    :param crs: *(optional)* The coordinate system of the given coordinates. Defaults to WGS84.
    :param session: *(optional)* A requests session.
    :return: A BaiduPanorama object if a panorama was found, or None.
    """

    x, y = _convert_to_bd09mc(coord1, coord2, crs)
    response = api.find_panorama(x, y, session)
    return parse_panorama_response(response)


async def find_panorama_async(coord1: float, coord2: float, session: ClientSession,
                              crs: Crs = Crs.WGS84) -> Optional[BaiduPanorama]:
    x, y = _convert_to_bd09mc(coord1, coord2, crs)
    response = await api.find_panorama_async(x, y, session)
    return parse_panorama_response(response)


def _convert_to_bd09mc(coord1: float, coord2: float, crs: Crs) -> Tuple[float, float]:
    if crs == Crs.WGS84:
        x, y = wgs84_to_bd09mc(coord1, coord2)
    elif crs == Crs.GCJ02:
        x, y = gcj02_to_bd09mc(coord1, coord2)
    elif crs == Crs.BD09:
        x, y = bd09_to_bd09mc(coord1, coord2)
    elif crs == Crs.BD09MC:
        x, y = coord1, coord2
    else:
        raise ValueError("Unsupported CRS")
    return x, y


def find_panorama_by_id(panoid: str, session: Session = None) \
        -> Optional[BaiduPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The panorama ID.
    :param session: *(optional)* A requests session.
    :return: A BaiduPanorama object if a panorama with this ID was found, or None.
    """
    response = api.find_panorama_by_id(panoid, session)
    return parse_panorama_response(response)


async def find_panorama_by_id_async(panoid: str, session: ClientSession) \
        -> Optional[BaiduPanorama]:
    response = await api.find_panorama_by_id_async(panoid, session)
    return parse_panorama_response(response)


def get_inter_metadata(iid: str, session: Session = None) -> Optional[InteriorMetadata]:
    """
    Fetches metadata of a set of interior/tripod (``inter``) panoramas.

    :param iid: The ``inter`` ID.
    :param session: *(optional)* A requests session.
    :return: The metadata.
    """
    response = api.get_inter_metadata(iid, session)
    return parse_inter_response(response)


async def get_inter_metadata_async(iid: str, session: ClientSession) -> Optional[InteriorMetadata]:
    response = await api.get_inter_metadata_async(iid, session)
    return parse_inter_response(response)


def get_panorama(pano: BaiduPanorama, zoom: int = 3) -> Image.Image:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama to download.
    :param zoom: *(optional)* Image size; 0 is lowest, 3 is highest. The dimensions of a zoom level of a
        specific panorama depend on the camera used. If the requested zoom level does not exist,
        the highest available level will be downloaded. Defaults to 3.
    :return: A PIL image containing the panorama.
    """
    zoom = _validate_get_panorama_params(pano, zoom)
    return get_equirectangular_panorama(
        pano.image_sizes[zoom].x, pano.image_sizes[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom))


async def get_panorama_async(pano: BaiduPanorama, session: ClientSession, zoom: int = 3) -> Image.Image:
    zoom = _validate_get_panorama_params(pano, zoom)
    return await get_equirectangular_panorama_async(
        pano.image_sizes[zoom].x, pano.image_sizes[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom),
        session)


def download_panorama(pano: BaiduPanorama, path: str, zoom: int = 3, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file. If the chosen format is JPEG, Exif and XMP GPano metadata are included.

    (``PosePitchDegrees`` and ``PoseRollDegrees`` are not set because I've been unable to work out
    the order of operations. Rotations are my arch nemesis and there is only so much time I'm
    willing to waste on this.)

    :param pano: The panorama to download.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 3 is highest. The dimensions of a zoom level of a
        specific panorama depend on the camera used. If the requested zoom level does not exist,
        the highest available level will be downloaded. Defaults to 3.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}
    image = get_panorama(pano, zoom=zoom)
    save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))


async def download_panorama_async(pano: BaiduPanorama, path: str, session: ClientSession,
                                  zoom: int = 3, pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}
    image = await get_panorama_async(pano, session, zoom=zoom)
    save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))


def _build_output_metadata_object(pano: BaiduPanorama, image: Image.Image) -> OutputMetadata:
    if pano.heading:
        heading = -(pano.heading - math.pi / 2)
    else:
        heading = None
    return OutputMetadata(
        width=image.width,
        height=image.height,
        panoid=str(pano.id),
        lat=pano.lat,
        lon=pano.lon,
        creator=pano.creator if pano.creator else "Baidu",
        is_equirectangular=True,
        altitude=pano.elevation,
        date=pano.date,
        heading=heading,
    )


def _validate_get_panorama_params(pano: BaiduPanorama, zoom: int) -> int:
    if not pano.image_sizes:
        raise ValueError("pano.image_sizes is None.")
    zoom = max(0, min(zoom, len(pano.image_sizes) - 1))
    return zoom


def _generate_tile_list(pano: BaiduPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    img_size = pano.image_sizes[zoom]
    tile_width = pano.tile_size.x
    tile_height = pano.tile_size.y
    cols = math.ceil(img_size.x / tile_width)
    rows = math.ceil(img_size.y / tile_height)

    IMAGE_URL = "https://mapsv1.bdimg.com/?qt=pdata&sid={0:}&pos={1:}_{2:}&z={3:}"

    coords = list(itertools.product(range(cols), range(rows)))
    tiles = [Tile(x, y, IMAGE_URL.format(pano.id, y, x, zoom + 1)) for x, y in coords]
    return tiles

