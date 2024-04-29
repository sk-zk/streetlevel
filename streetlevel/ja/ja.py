from typing import Optional, List, Tuple, Union

from PIL import Image
from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import JaPanorama
from .parse import parse_panorama_radius_response, parse_panorama_id_response
from ..dataclasses import Tile
from ..util import download_tiles, download_tiles_async, CubemapStitchingMethod, stitch_cubemap_faces, \
    save_cubemap_panorama, stitch_cubemap_face


def find_panorama(lat: float, lon: float, radius: int = 100, session: Session = None) -> Optional[JaPanorama]:
    """
    Searches for a panorama within a radius around a point.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param radius: *(optional)* Search radius in meters, max. 5000(?). Defaults to 100.
    :param session: *(optional)* A requests session.
    :return: A JaPanorama if a panorama was found, or None.
    """
    response = api.find_panorama(lat, lon, radius, session)
    return parse_panorama_radius_response(response)


async def find_panorama_async(lat: float, lon: float, session: ClientSession,
                              radius: int = 100) -> Optional[JaPanorama]:
    response = await api.find_panorama_async(lat, lon, session, radius)
    return parse_panorama_radius_response(response)


def find_panorama_by_id(panoid: int, session: Session = None) -> Optional[JaPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: A JaPanorama object if a panorama with this ID was found, or None.
    """
    response = api.find_panorama_by_id(panoid, session)
    return parse_panorama_id_response(response)


async def find_panorama_by_id_async(panoid: int, session: ClientSession) -> Optional[JaPanorama]:
    response = await api.find_panorama_by_id_async(panoid, session)
    return parse_panorama_id_response(response)


def get_panorama(pano: JaPanorama, zoom: int = 0,
                 stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW) \
        -> Union[List[Image.Image], Image.Image]:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama.
    :param zoom: *(optional)* Image size; 0 is high, 1 is low. Defaults to 0.
    :param stitching_method: *(optional)* Whether and how the faces of the cubemap are stitched into one
        image. Defaults to ``ROW``.
    :return: A PIL image or a list of six PIL images depending on ``stitching_method``.
    """
    zoom = _validate_get_panorama_params(pano, zoom)
    face_tiles, cols, rows = _generate_tile_list(pano, zoom)
    tile_images = _download_tiles(face_tiles)
    return _stitch_panorama(tile_images, cols, rows, stitching_method=stitching_method)


async def get_panorama_async(pano: JaPanorama, session: ClientSession, zoom: int = 0,
                             stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW) \
        -> Union[List[Image.Image], Image.Image]:
    zoom = _validate_get_panorama_params(pano, zoom)
    face_tiles, cols, rows = _generate_tile_list(pano, zoom)
    tile_images = await _download_tiles_async(face_tiles, session)
    return _stitch_panorama(tile_images, cols, rows, stitching_method=stitching_method)


def download_panorama(pano: JaPanorama, path: str, zoom: int = 0,
                      stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW,
                      pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.

    :param pano: The panorama.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is high, 1 is low. Defaults to 0.
    :param stitching_method: *(optional)* Whether and how the faces of the cubemap are stitched into one
        image. Defaults to ``ROW``.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}

    output = get_panorama(pano, zoom=zoom, stitching_method=stitching_method)
    save_cubemap_panorama(output, path, pil_args)


async def download_panorama_async(pano: JaPanorama, path: str, session: ClientSession, zoom: int = 0,
                                  stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW,
                                  pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}

    output = await get_panorama_async(pano, session, zoom=zoom, stitching_method=stitching_method)
    save_cubemap_panorama(output, path, pil_args)


def _validate_get_panorama_params(pano, zoom):
    if not pano.pano_url:
        raise ValueError("pano_url is None; please call find_panorama_by_id to fetch this info")
    zoom = min(1, max(zoom, 0))
    return zoom


def _generate_tile_list(pano: JaPanorama, zoom: int) -> Tuple[List[List[Tile]], int, int]:
    if not (zoom == 0 or zoom == 1):
        raise ValueError("Unsupported zoom level")

    cols = 2 if zoom == 1 else 4
    rows = 2 if zoom == 1 else 4

    tiles = []
    for face_url_name in ["f", "r", "b", "l", "u", "d"]:
        face_tiles = []
        for row_idx in range(0, rows):
            for col_idx in range(0, cols):
                blur_key_str = f".{pano.blur_key}" if pano.blur_key else ""
                face_tiles.append(Tile(col_idx, row_idx,
                                       f"{pano.pano_url}/mres_{face_url_name}/l{zoom+1}/"
                                       f"l{zoom+1}_{face_url_name}_{row_idx+1}_{col_idx+1}{blur_key_str}.jpg"))
        tiles.append(face_tiles)
    return tiles, cols, rows


def _download_tiles(face_tiles: List[List[Tile]]) -> List[dict]:
    faces = []
    for face in face_tiles:
        faces.append(download_tiles(face))
    return faces


async def _download_tiles_async(face_tiles: List[List[Tile]], session: ClientSession) -> List[dict]:
    faces = []
    for face in face_tiles:
        faces.append(await download_tiles_async(face, session))
    return faces


def _stitch_panorama(tile_images: List[dict], cols: int, rows: int,
                     stitching_method: CubemapStitchingMethod) -> Union[List[Image.Image], Image.Image]:
    stitched_faces = []
    for tiles in tile_images:
        stitched_face = stitch_cubemap_face(tiles, 512, cols, rows)
        stitched_faces.append(stitched_face)
    return stitch_cubemap_faces(stitched_faces, stitched_faces[0].size[0], stitching_method)
