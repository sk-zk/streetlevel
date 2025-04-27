import itertools
import math
from typing import Optional, List, Union, Tuple

import numpy as np
from aiohttp import ClientSession
from PIL import Image
from google.protobuf.message import DecodeError
from requests import Session

from . import api
from .model import Model
from .panorama import NaverPanorama, Neighbors
from .parse import parse_panorama, parse_nearby, parse_historical, parse_neighbors
from ..dataclasses import Tile, Size
from ..exif import save_with_metadata, OutputMetadata
from ..util import download_tiles, CubemapStitchingMethod, stitch_cubemap_faces, download_tiles_async, \
    save_cubemap_panorama, get_image, get_image_async, stitch_cubemap_face, get_equirectangular_panorama, \
    get_equirectangular_panorama_async


def find_panorama_by_id(panoid: str, language: str = "en",
                        neighbors: bool = True, historical: bool = True, depth: bool = False,
                        session: Session = None) -> Optional[NaverPanorama]:
    """
    Fetches metadata of a specific panorama.

    Note that ``panorama_type``, ``pitch`` and ``roll`` will be wrong if this is a 3D panorama because
    Naver has yet to update this endpoint.

    :param panoid: The pano ID.
    :param language: *(optional)* Language of ``description`` and ``title`` fields; accepted values are
        ``ko`` (Korean), ``en`` (English), ``ja`` (Japanese) and ``zh`` (Simplified Chinese).
    :param neighbors: *(optional)* Whether an additional network request is made to fetch nearby panoramas.
        Defaults to True.
    :param historical: *(optional)* Whether an additional network request is made to fetch metadata of
        historical panoramas. Defaults to True.
    :param depth: *(optional)* Whether an additional network request is made to fetch the depth map.
        Defaults to False.
    :param session: *(optional)* A requests session.
    :return: A NaverPanorama object if a panorama with this ID exists, or None.
    """
    response = api.find_panorama_by_id(panoid, language, session)

    if "errors" in response:
        return None

    pano = parse_panorama(response)
    if neighbors:
        pano.neighbors = get_neighbors(pano.id, session=session)
    if historical:
        pano.historical = get_historical(pano.timeline_id, session=session)
    if depth:
        pano.depth = get_depth(pano.id, session=session)
    return pano


async def find_panorama_by_id_async(panoid: str, session: ClientSession, language: str = "en", neighbors: bool = True,
                                    historical: bool = True, depth: bool = False) -> Optional[NaverPanorama]:
    response = await api.find_panorama_by_id_async(panoid, language, session)

    if "errors" in response:
        return None

    pano = parse_panorama(response)
    if neighbors:
        pano.neighbors = await get_neighbors_async(pano.id, session)
    if historical:
        pano.historical = await get_historical_async(pano.timeline_id, session)
    if depth:
        pano.depth = await get_depth_async(pano.id, session)
    return pano


def find_panorama(lat: float, lon: float, neighbors: bool = True, historical: bool = True, depth: bool = False,
                  session: Session = None) -> Optional[NaverPanorama]:
    """
    Searches for a panorama near the given point.

    Aerial and underwater panoramas are ignored by this API call.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param neighbors: *(optional)* Whether an additional network request is made to fetch nearby panoramas.
        Defaults to True.
    :param historical: *(optional)* Whether an additional network request is made to fetch metadata of
        historical panoramas. Defaults to True.
    :param depth: *(optional)* Whether an additional network request is made to fetch the depth map.
        Defaults to False.
    :param session: *(optional)* A requests session.
    :return: A NaverPanorama object if a panorama was found, or None.
    """
    response = api.find_panorama(lat, lon, session)

    if "error" in response or len(response["features"]) == 0:
        return None

    pano = parse_nearby(response)
    if neighbors:
        pano.neighbors = get_neighbors(pano.id, session=session)
    if historical:
        pano.historical = get_historical(pano.id, session=session)
    if depth:
        pano.depth = get_depth(pano.id, session=session)
    return pano


async def find_panorama_async(lat: float, lon: float, session: ClientSession, neighbors: bool = True,
                              historical: bool = True, depth: bool = False) -> Optional[NaverPanorama]:
    response = await api.find_panorama_async(lat, lon, session)

    if "error" in response or len(response["features"]) == 0:
        return None

    pano = parse_nearby(response)
    if neighbors:
        pano.neighbors = await get_neighbors_async(pano.id, session)
    if historical:
        pano.historical = await get_historical_async(pano.id, session)
    if depth:
        pano.depth = await get_depth_async(pano.id, session)
    return pano


def get_historical(panoid: str, session: Session = None) -> List[NaverPanorama]:
    """
    Fetches older panoramas at the location of the given panorama.

    :param panoid: The pano ID. For reasons unbeknownst to mankind, only panoramas older than the given one
        are returned, so to retrieve all available dates at a location, the ID of the most recent panorama
        must be used. This is the ``timeline_id`` returned by ``find_panorama_by_id``.
    :param session: *(optional)* A requests session.
    :return: A list of NaverPanorama objects.
    """
    response = api.get_historical(panoid, session=session)

    if "errors" in response:
        return []

    return parse_historical(response, panoid)


async def get_historical_async(panoid: str, session: ClientSession) -> List[NaverPanorama]:
    response = await api.get_historical_async(panoid, session)

    if "errors" in response:
        return []

    return parse_historical(response, panoid)


def get_neighbors(panoid: str, session: Session = None) -> Neighbors:
    """
    Fetches neighbors of a panorama.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: A Neighbors object.
    """
    response = api.get_neighbors(panoid, session=session)

    if "errors" in response:
        return Neighbors([], [])

    return parse_neighbors(response, panoid)


async def get_neighbors_async(panoid: str, session: ClientSession) -> Neighbors:
    response = await api.get_neighbors_async(panoid, session)

    if "errors" in response:
        return Neighbors([], [])

    return parse_neighbors(response, panoid)


def get_panorama(pano: NaverPanorama, zoom: int = 2, equirect=False,
                 stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW) \
        -> Union[List[Image.Image], Image.Image]:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. Defaults to 2. If 2 is unavailable, 1 will be
        downloaded instead.
    :param equirect: *(optional)* Whether the panorama should be downloaded in equirectangular projection instead of
        a cubemap. Only available for 3D imagery. Defaults to False.
    :param stitching_method: *(optional)* Whether and how the faces of the cubemap are stitched into one
        image when downloading as cubemap. Defaults to ``ROW``.
    :return: A PIL image or a list of six PIL images depending on ``equirect`` and ``stitching_method``.
    """
    zoom = _validate_zoom(pano, zoom)
    if equirect:
        if not pano.has_equirect:
            raise ValueError("This panorama cannot be downloaded in equirectangular projection.")
        cols = 4 * int(math.pow(2, zoom))
        rows = 2 * int(math.pow(2, zoom))
        return get_equirectangular_panorama(
            pano.tile_size.x * cols, pano.tile_size.y * rows,
            pano.tile_size, _generate_tile_list_equirect(pano, zoom))
    else:
        if zoom == 0:
            return _get_zoom_0_cubemap(pano, stitching_method)
        face_tiles, cols, rows = _generate_tile_list_cubemap(pano.id, zoom)
        tile_images = _download_tiles(face_tiles)
        return _stitch_panorama(tile_images, cols, rows, stitching_method=stitching_method)


async def get_panorama_async(pano: NaverPanorama, session: ClientSession, zoom: int = 2, equirect=False,
                             stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW) \
        -> Union[List[Image.Image], Image.Image]:
    zoom = _validate_zoom(pano, zoom)
    if equirect:
        if not pano.has_equirect:
            raise ValueError("This panorama cannot be downloaded in equirectangular projection.")
        cols = 4 * int(math.pow(2, zoom))
        rows = 2 * int(math.pow(2, zoom))
        return await get_equirectangular_panorama_async(
            512 * cols, 512 * rows, Size(512, 512),
            _generate_tile_list_equirect(pano, zoom), session)
    else:
        if zoom == 0:
            return await _get_zoom_0_cubemap_async(pano, session, stitching_method)
        face_tiles, cols, rows = _generate_tile_list_cubemap(pano.id, zoom)
        tile_images = await _download_tiles_async(face_tiles, session)
        return _stitch_panorama(tile_images, cols, rows, stitching_method=stitching_method)


def download_panorama(pano: NaverPanorama, path: str, zoom: int = 2, equirect=False,
                      stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW,
                      pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file. If the chosen format is JPEG, Exif and XMP GPano metadata are included.

    :param pano: The panorama.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. Defaults to 2. If 2 is unavailable, 1 will be
        downloaded instead.
    :param equirect: *(optional)* Whether the panorama should be downloaded in equirectangular projection instead of
        a cubemap. Only available for 3D imagery. Defaults to False.
    :param stitching_method: *(optional)* Whether and how the faces of the cubemap are stitched into one
        image when downloading as cubemap. Defaults to ``ROW``.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if pil_args is None:
        pil_args = {}

    image = get_panorama(pano, zoom=zoom, equirect=equirect,
                         stitching_method=stitching_method)
    if equirect:
        save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))
    else:
        save_cubemap_panorama(image, path, pil_args)


async def download_panorama_async(pano: NaverPanorama, path: str, session: ClientSession, zoom: int = 2, equirect=False,
                                  stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW,
                                  pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}

    image = await get_panorama_async(pano, session, zoom=zoom, equirect=equirect,
                                     stitching_method=stitching_method)
    if equirect:
        save_with_metadata(image, path, pil_args, _build_output_metadata_object(pano, image))
    else:
        save_cubemap_panorama(image, path, pil_args)


def _build_output_metadata_object(pano: NaverPanorama, image: Image.Image) -> OutputMetadata:
    return OutputMetadata(
        width=image.width,
        height=image.height,
        panoid=pano.id,
        lat=pano.lat,
        lon=pano.lon,
        creator="Naver",
        is_equirectangular=True,
        altitude=pano.altitude,
        date=pano.date,
        heading=math.pi - pano.heading,
        pitch=pano.pitch,
        roll=pano.roll,
    )


def get_depth(panoid: str, session: Session = None) -> np.ndarray:
    """
    Fetches the legacy depth map of a panorama.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: The depth map of the faces in the order front, right, back, left, top, bottom.
    """
    depth_json = api.get_depth(panoid, session=session)
    return _parse_depth(depth_json)


async def get_depth_async(panoid: str, session: ClientSession) -> np.ndarray:
    depth_json = await api.get_depth_async(panoid, session)
    return _parse_depth(depth_json)


def get_model(panoid: str, session: Session = None) -> Optional[Model]:
    """
    Fetches the 3D model of the panorama. Only available if the panorama type is ``MESH_EQUIRECT``.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: The vertices and faces of the model, or None if this panorama does not have a 3D model.
    """
    try:
        pb_mesh = api.get_mesh(panoid, session)
    except DecodeError:
        return None
    return Model(
        np.reshape(pb_mesh.vertices, (len(pb_mesh.vertices)//3,3)),
        np.reshape(pb_mesh.faces, (len(pb_mesh.faces)//3,3))
    )


async def get_model_async(panoid: str, session: ClientSession):
    try:
        pb_mesh = await api.get_mesh_async(panoid, session)
    except DecodeError:
        return None
    return Model(
        np.reshape(pb_mesh.vertices, (len(pb_mesh.vertices)//3,3)),
        np.reshape(pb_mesh.faces, (len(pb_mesh.faces)//3,3))
    )

def _parse_depth(depth_json: dict) -> np.ndarray:
    depth = [float(n) for n in depth_json["depthmap"].split(",")]
    depth_faces = []
    for i in [0, 1, 2, 3, 5, 4]:
        # this order ^ is intentional, it reverses the top and bottom face for consistency with everything else
        depth_faces.append(np.array(depth[i * 4225:(i + 1) * 4225]).reshape(65, 65))
    return np.array(depth_faces)


def _get_zoom_0_cubemap(pano: NaverPanorama,
                        stitching_method: CubemapStitchingMethod) -> Union[List[Image.Image], Image.Image]:
    FACE_SIZE = 256
    image = get_image(f"https://panorama.pstatic.net/image/{pano.id}/512/P")
    faces = [image.crop((i*FACE_SIZE, 0, (i+1)*FACE_SIZE, FACE_SIZE)) for i in [1, 2, 3, 0, 5, 4]]
    return stitch_cubemap_faces(faces, FACE_SIZE, stitching_method)


async def _get_zoom_0_cubemap_async(pano: NaverPanorama, session: ClientSession,
                                    stitching_method: CubemapStitchingMethod) -> Union[List[Image.Image], Image.Image]:
    FACE_SIZE = 256
    image = await get_image_async(f"https://panorama.pstatic.net/image/{pano.id}/512/P", session)
    faces = [image.crop((i*FACE_SIZE, 0, (i+1)*FACE_SIZE, FACE_SIZE)) for i in [1, 2, 3, 0, 5, 4]]
    return stitch_cubemap_faces(faces, FACE_SIZE, stitching_method)


def _validate_zoom(pano: NaverPanorama, zoom: int) -> int:
    if not pano.max_zoom:
        if zoom > 1:
            raise ValueError("max_zoom is None; please call find_panorama_by_id to fetch this info")
        else:
            return max(0, zoom)
    else:
        return max(0, min(zoom, pano.max_zoom))


def _generate_tile_list_cubemap(panoid: str, zoom: int) -> Tuple[List[List[Tile]], int, int]:
    if not (zoom == 1 or zoom == 2):
        raise ValueError("Unsupported zoom level")

    cols = zoom * 2
    rows = zoom * 2
    size_letter = "M" if zoom == 1 else "L"

    tiles = []
    for face_url_name in ["f", "r", "b", "l", "u", "d"]:
        face_tiles = []
        for row_idx in range(0, rows):
            for col_idx in range(0, cols):
                face_tiles.append(Tile(col_idx, row_idx,
                                       f"https://panorama.pstatic.net/image/{panoid}/512/{size_letter}/"
                                       f"{face_url_name}/{col_idx+1}/{row_idx+1}"))
        tiles.append(face_tiles)
    return tiles, cols, rows


def _generate_tile_list_equirect(pano: NaverPanorama, zoom: int) -> List[Tile]:
    """
    Generates a list of a panorama's tiles and the URLs pointing to them.
    """
    cols = 4 * int(math.pow(2, zoom))
    rows = 2 * int(math.pow(2, zoom))

    IMAGE_URL = "https://panorama.pstatic.net/imageV3/{0:}/{3:}/{1:}/{2:}"

    coords = list(itertools.product(range(cols), range(rows)))
    tiles = [Tile(x, y, IMAGE_URL.format(pano.id, x+1, y+1, zoom)) for x, y in coords]
    return tiles


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
