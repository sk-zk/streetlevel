import itertools
from typing import List, Optional

from aiohttp import ClientSession
from PIL import Image
from requests import Session

from .api import MapyApi
from .panorama import MapyPanorama
from .parse import parse_pan_info_dict, parse_neighbors_response, parse_getbest_response
from ..dataclasses import Tile, Link
from ..exif import save_with_metadata, OutputMetadata
from ..util import get_equirectangular_panorama, get_equirectangular_panorama_async, get_image, get_image_async

api = MapyApi()


def find_panorama(lat: float, lon: float,
                  radius: float = 100.0,
                  year: Optional[int] = None,
                  links: bool = True,
                  historical: bool = True) -> Optional[MapyPanorama]:
    """
    Searches for a panorama within a radius around a point.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param radius: *(optional)* Search radius in meters. Defaults to 100.
    :param year: *(optional)* If given, searches for a specific year. Otherwise, the most recent panorama is returned.
    :param links: *(optional)* Whether an additional network request is made to fetch linked panoramas.
        Defaults to True.
    :param historical: *(optional)* Whether additional network requests are made to fetch metadata of
        panoramas from other years. Defaults to True.
    :return: A MapyPanorama object if a panorama was found, or None.
    """
    options, radius = _validate_find_panorama_params(radius, year)
    response = api.getbest(lat, lon, radius, options=options)
    pano = parse_getbest_response(response)

    if pano:
        if links:
            pano.links = get_links(pano.id, year=pano.date.year)
        if historical:
            _append_historical(pano, response["result"]["panInfo"], lat, lon)

    return pano


async def find_panorama_async(lat: float, lon: float,
                              radius: float = 100.0,
                              year: Optional[int] = None,
                              links: bool = True,
                              historical: bool = True) -> Optional[MapyPanorama]:
    options, radius = _validate_find_panorama_params(radius, year)
    response = await api.getbest_async(lat, lon, radius, options=options)
    pano = parse_getbest_response(response)

    if pano:
        if links:
            pano.links = await get_links_async(pano.id, year=pano.date.year)
        if historical:
            await _append_historical_async(pano, response["result"]["panInfo"], lat, lon)

    return pano


def find_panorama_by_id(panoid: int,
                        links: bool = True,
                        historical: bool = True) -> Optional[MapyPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The pano ID.
    :param links: *(optional)* Whether an additional network request is made to fetch linked panoramas.
        Defaults to True.
    :param historical: *(optional)* Whether additional network requests are made to fetch metadata of
        panoramas from other years. Defaults to True.
    :return: A MapyPanorama object if a panorama with this ID exists, or None.
    """
    response = api.detail(panoid)

    if response["status"] != 200:
        return None

    pan_info = response["result"]
    pano = parse_pan_info_dict(pan_info)

    if links:
        pano.links = get_links(pano.id, year=pano.date.year)
    if historical:
        _append_historical(pano, pan_info, pano.lat, pano.lon)

    return pano


async def find_panorama_by_id_async(panoid: int,
                                    links: bool = True,
                                    historical: bool = True) -> Optional[MapyPanorama]:
    response = await api.detail_async(panoid)

    if response["status"] != 200:
        return None

    pan_info = response["result"]
    pano = parse_pan_info_dict(pan_info)

    if links:
        pano.links = await get_links_async(pano.id, year=pano.date.year)
    if historical:
        await _append_historical_async(pano, pan_info, pano.lat, pano.lon)

    return pano


def get_links(panoid: int, year: Optional[int] = None) -> List[Link]:
    """
    Fetches linked panoramas.

    :param panoid: The pano ID.
    :param year: *(optional)* If given, fetches links for a specific year. Otherwise, the most recent coverage
        is returned.
    :return: A list of nearby panoramas.
    """
    if year is None:
        options = None
    else:
        options = {"year": year}

    response = api.getneighbours(panoid, options)
    return parse_neighbors_response(response)


async def get_links_async(panoid: int, year: Optional[int] = None) -> List[Link]:
    if year is None:
        options = None
    else:
        options = {"year": year}

    response = await api.getneighbours_async(panoid, options)
    return parse_neighbors_response(response)


def get_panorama(pano: MapyPanorama, zoom: int = 2) -> Image.Image:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. If 2 is not available, 1 will be downloaded.
        Defaults to 2.
    :return: A PIL image containing the panorama.
    """
    zoom = max(0, min(zoom, pano.max_zoom))

    if zoom == 0:
        return _get_zoom_0(pano)

    return get_equirectangular_panorama(
        pano.tile_size.x * pano.num_tiles[zoom].x,
        pano.tile_size.y * pano.num_tiles[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom))


async def get_panorama_async(pano: MapyPanorama, session: ClientSession, zoom: int = 2) -> Image.Image:
    zoom = max(0, min(zoom, pano.max_zoom))

    if zoom == 0:
        return await _get_zoom_0_async(pano, session)

    return await get_equirectangular_panorama_async(
        pano.tile_size.x * pano.num_tiles[zoom].x,
        pano.tile_size.y * pano.num_tiles[zoom].y,
        pano.tile_size, _generate_tile_list(pano, zoom),
        session)


def download_panorama(pano: MapyPanorama, path: str, zoom: int = 2, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file. If the chosen format is JPEG, Exif and XMP GPano metadata are included.

    :param pano: The panorama.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. If 2 is not available, 1 will be downloaded.
        Defaults to 2.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}
    image = get_panorama(pano, zoom=zoom)
    save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))


async def download_panorama_async(pano: MapyPanorama, path: str, session: ClientSession,
                                  zoom: int = 2, pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}
    image = await get_panorama_async(pano, session, zoom=zoom)
    save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))


def _build_output_metadata_object(pano: MapyPanorama, image: Image.Image) -> OutputMetadata:
    return OutputMetadata(
        width=image.width,
        height=image.height,
        panoid=str(pano.id),
        lat=pano.lat,
        lon=pano.lon,
        creator=pano.provider,
        is_equirectangular=True,
        altitude=pano.elevation,
        date=str(pano.date),
        heading=0, # north is already in the center of the image
        pitch=pano.pitch,
        roll=pano.roll,
    )


def _validate_find_panorama_params(radius, year):
    radius = float(radius)
    if year is None:
        options = None
    else:
        options = {'year': year, 'nopenalties': True}
    return options, radius


def _append_historical(pano, pan_info, lat, lon):
    for year in pan_info["timeline"]:
        if pano.date.year == year:
            continue
        historical_pano = find_panorama(lat, lon, 50.0, year=year,
                                        historical=False, links=False)
        pano.historical.append(historical_pano)


async def _append_historical_async(pano, pan_info, lat, lon):
    for year in pan_info["timeline"]:
        if pano.date.year == year:
            continue
        historical_pano = await find_panorama_async(lat, lon, 50.0, year=year,
                                                    historical=False, links=False)
        pano.historical.append(historical_pano)


def _get_zoom_0(pano: MapyPanorama, session: Session = None) -> Image.Image:
    return get_image(_generate_tile_list(pano, 0)[0].url, session=session)


async def _get_zoom_0_async(pano: MapyPanorama, session: ClientSession) -> Image.Image:
    return await get_image_async(_generate_tile_list(pano, 0)[0].url, session)


def _generate_tile_list(pano: MapyPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    file_mask = pano.file_mask.replace("xx", "{0:02x}") \
        .replace("yy", "{1:02x}") \
        .replace("zz", "{2:02x}")
    url = f"https://panorama-mapserver.mapy.cz/panorama/" \
          f"{pano.domain_prefix}/{pano.uri_path}/{file_mask}"

    coords = list(itertools.product(range(pano.num_tiles[zoom].x), range(pano.num_tiles[zoom].y)))
    tiles = [Tile(x, y, url.format(x, y, zoom)) for x, y in coords]
    return tiles
