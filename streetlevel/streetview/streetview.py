from aiohttp import ClientSession
import itertools
import math
from PIL import Image
from requests import Session
from typing import List, Optional

from . import api
from .panorama import StreetViewPanorama
from .parse import parse_coverage_tile_response, parse_panorama_id_response, \
    parse_panorama_radius_response
from .util import is_third_party_panoid
from ..dataclasses import Tile
from ..exif import save_with_metadata, OutputMetadata, add_metadata
from ..geo import wgs84_to_tile_coord
from ..util import get_equirectangular_panorama, get_equirectangular_panorama_async, get_image, get_image_async, \
    download_file, download_file_async


def find_panorama(lat: float, lon: float, radius: int = 50, locale: str = "en",
                  search_third_party: bool = False, session: Session = None) -> Optional[StreetViewPanorama]:
    """
    Searches for a panorama within a radius around a point.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param radius: *(optional)* Search radius in meters. Defaults to 50.
    :param locale: *(optional)* Desired language of the location's address as IETF code.
      Defaults to ``en``.
    :param search_third_party: *(optional)* Whether to search for third-party panoramas
      rather than official ones. Defaults to false.
    :param session: *(optional)* A requests session.
    :return: A StreetViewPanorama object if a panorama was found, or None.
    """

    # TODO
    # the `SingleImageSearch` call returns a different kind of depth data
    # than `photometa`; need to deal with that at some point

    response = api.find_panorama(lat, lon, radius=radius, download_depth=False,
                                 locale=locale, search_third_party=search_third_party, session=session)
    return parse_panorama_radius_response(response)


async def find_panorama_async(lat: float, lon: float, session: ClientSession, radius: int = 50,
                              locale: str = "en", search_third_party: bool = False) -> Optional[StreetViewPanorama]:
    # TODO
    # the `SingleImageSearch` call returns a different kind of depth data
    # than `photometa`; need to deal with that at some point
    response = await api.find_panorama_async(lat, lon, session, radius=radius, download_depth=False,
                                             locale=locale, search_third_party=search_third_party)
    return parse_panorama_radius_response(response)


def find_panorama_by_id(panoid: str, download_depth: bool = False, locale: str = "en",
                        session: Session = None) -> Optional[StreetViewPanorama]:
    """
    Fetches metadata of a specific panorama.

    Unfortunately, `as mentioned on this page
    <https://developers.google.com/maps/documentation/tile/streetview#panoid_response>`_,
    pano IDs are not stable, so a request that works today may return nothing a few months into the future.

    :param panoid: The pano ID.
    :param download_depth: Whether to download and parse the depth map.
    :param locale: Desired language of the location's address as IETF code.
    :param session: *(optional)* A requests session.
    :return: A StreetViewPanorama object if a panorama with this ID exists, or None.
    """
    response = api.find_panorama_by_id(panoid, download_depth=download_depth,
                                       locale=locale, session=session)
    return parse_panorama_id_response(response)


async def find_panorama_by_id_async(panoid: str, session: ClientSession, download_depth: bool = False,
                                    locale: str = "en") -> Optional[StreetViewPanorama]:
    response = await api.find_panorama_by_id_async(panoid, session,
                                                   download_depth=download_depth, locale=locale)
    return parse_panorama_id_response(response)


def get_coverage_tile(tile_x: int, tile_y: int, session: Session = None) -> List[StreetViewPanorama]:
    """
    Fetches Street View coverage on a specific map tile. Coordinates are in Slippy Map aka XYZ format
    at zoom level 17.

    When viewing Google Maps with satellite imagery in globe view and zooming into a spot,
    it makes this API call. This is useful because 1) it allows for fetching coverage for a whole area, and
    2) there are various hidden/removed locations which cannot be found by any other method
    (unless you access them by pano ID directly).

    This function returns ID, position, elevation, orientation, and links within the tile of the most recent coverage.
    The rest of the metadata, such as historical panoramas or links across tiles, must be fetched manually one by one.

    :param tile_x: X coordinate of the tile.
    :param tile_y: Y coordinate of the tile.
    :param session: *(optional)* A requests session.
    :return: A list of StreetViewPanoramas. If no coverage was returned by the API, the list is empty.
    """
    response = api.get_coverage_tile(tile_x, tile_y, session)
    return parse_coverage_tile_response(response)


async def get_coverage_tile_async(tile_x: int, tile_y: int, session: ClientSession) -> List[StreetViewPanorama]:
    response = await api.get_coverage_tile_async(tile_x, tile_y, session)
    return parse_coverage_tile_response(response)


def get_coverage_tile_by_latlon(lat: float, lon: float, session: Session = None) -> List[StreetViewPanorama]:
    """
    Same as :func:`get_coverage_tile <get_coverage_tile>`, but for fetching the tile on which a point is located.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param session: *(optional)* A requests session.
    :return: A list of StreetViewPanoramas. If no coverage was returned by the API, the list is empty.
    """
    tile_coord = wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(tile_coord[0], tile_coord[1], session=session)


async def get_coverage_tile_by_latlon_async(lat: float, lon: float, session: ClientSession) \
        -> List[StreetViewPanorama]:
    tile_coord = wgs84_to_tile_coord(lat, lon, 17)
    return await get_coverage_tile_async(tile_coord[0], tile_coord[1], session)


def download_panorama(pano: StreetViewPanorama, path: str, zoom: int = 5, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file. If the chosen format is JPEG, Exif and XMP GPano metadata are included.

    :param pano: The panorama to download.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 5 is highest. The dimensions of a zoom level of a
        specific panorama depend on the camera used. If the requested zoom level does not exist,
        the highest available level will be downloaded. Defaults to 5.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pano.is_third_party:
        zoom = _validate_get_panorama_params(pano, zoom)
        url = _build_sized_third_party_image_url(pano, zoom)
        download_file(url, path)
        add_metadata(path, _build_output_metadata_object(pano, pano.image_sizes[zoom].x, pano.image_sizes[zoom].y))
    else:
        if pil_args is None:
            pil_args = {}
        image = get_panorama(pano, zoom=zoom)
        save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image.width, image.height))


async def download_panorama_async(pano: StreetViewPanorama, path: str, session: ClientSession,
                                  zoom: int = 5, pil_args: dict = None) -> None:
    if pano.is_third_party:
        zoom = _validate_get_panorama_params(pano, zoom)
        url = _build_sized_third_party_image_url(pano, zoom)
        await download_file_async(url, path, session)
        add_metadata(path, _build_output_metadata_object(pano, pano.image_sizes[zoom].x, pano.image_sizes[zoom].y))
    else:
        if pil_args is None:
            pil_args = {}
        image = await get_panorama_async(pano, session, zoom=zoom)
        save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image.width, image.height))


def _build_sized_third_party_image_url(pano: StreetViewPanorama, zoom: int) -> str:
    width = str(pano.image_sizes[zoom].x)
    height = str(pano.image_sizes[zoom].y)
    url = f"https://lh3.ggpht.com/jsapi2/a/b/c/w{width}-h{height}/{pano.id}"
    return url


def _build_output_metadata_object(pano: StreetViewPanorama, width: int, height: int) -> OutputMetadata:
    return OutputMetadata(
        width=width,
        height=height,
        panoid=pano.id,
        lat=pano.lat,
        lon=pano.lon,
        creator=pano.uploader if pano.uploader is not None else "Google",
        is_equirectangular=True,
        altitude=pano.elevation,
        date=str(pano.date),
        heading=-pano.heading if pano.heading else None,
        pitch=pano.pitch,
        roll=pano.roll,
    )


def get_panorama(pano: StreetViewPanorama, zoom: int = 5) -> Image.Image:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama to download.
    :param zoom: *(optional)* Image size; 0 is lowest, 5 is highest. The dimensions of a zoom level of a
        specific panorama depend on the camera used. If the requested zoom level does not exist,
        the highest available level will be downloaded. Defaults to 5.
    :return: A PIL image containing the panorama.
    """
    zoom = _validate_get_panorama_params(pano, zoom)

    if pano.is_third_party:
        url = _build_sized_third_party_image_url(pano, zoom)
        return get_image(url)

    return get_equirectangular_panorama(
        pano.image_sizes[zoom].x, pano.image_sizes[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom))


async def get_panorama_async(pano: StreetViewPanorama, session: ClientSession, zoom: int = 5) -> Image.Image:
    zoom = _validate_get_panorama_params(pano, zoom)

    if pano.is_third_party:
        url = _build_sized_third_party_image_url(pano, zoom)
        return await get_image_async(url, session)

    return await get_equirectangular_panorama_async(
        pano.image_sizes[zoom].x, pano.image_sizes[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom),
        session)


def _validate_get_panorama_params(pano: StreetViewPanorama, zoom: int) -> int:
    if not pano.image_sizes:
        raise ValueError("pano.image_sizes is None.")
    zoom = max(0, min(zoom, len(pano.image_sizes) - 1))
    return zoom


def _generate_tile_list(pano: StreetViewPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    img_size = pano.image_sizes[zoom]
    tile_width = pano.tile_size.x
    tile_height = pano.tile_size.y
    cols = math.ceil(img_size.x / tile_width)
    rows = math.ceil(img_size.y / tile_height)

    IMAGE_URL = "https://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom={3:}&x={1:}&y={2:}"

    coords = list(itertools.product(range(cols), range(rows)))
    tiles = [Tile(x, y, IMAGE_URL.format(pano.id, x, y, zoom)) for x, y in coords]
    return tiles
