import math
from datetime import datetime
from typing import Optional, List, Union, Tuple

import numpy as np
from aiohttp import ClientSession
from PIL import Image
from requests import Session

from . import api
from .panorama import NaverPanorama, PanoramaType, Overlay, Neighbors
from ..dataclasses import Tile, Link
from ..util import download_tiles, CubemapStitchingMethod, stitch_cubemap_faces, download_tiles_async, \
    save_cubemap_panorama, get_image, get_image_async, stitch_cubemap_face


def find_panorama_by_id(panoid: str, language: str = "en",
                        neighbors: bool = True, historical: bool = True, depth: bool = False,
                        session: Session = None) -> Optional[NaverPanorama]:
    """
    Fetches metadata of a specific panorama.

    :param panoid: The pano ID.
    :param language: *(optional)* Language of ``description`` and ``title`` fields; accepted values are ``ko`` (Korean)
        and ``en`` (English).
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

    pano = _parse_panorama(response)
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

    pano = _parse_panorama(response)
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

    pano = _parse_nearby(response)
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

    pano = _parse_nearby(response)
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

    return _parse_historical(response, panoid)


async def get_historical_async(panoid: str, session: ClientSession) -> List[NaverPanorama]:
    response = await api.get_historical_async(panoid, session)

    if "errors" in response:
        return []

    return _parse_historical(response, panoid)


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

    return _parse_neighbors(response, panoid)


async def get_neighbors_async(panoid: str, session: ClientSession) -> Neighbors:
    response = await api.get_neighbors_async(panoid, session)

    if "errors" in response:
        return Neighbors([], [])

    return _parse_neighbors(response, panoid)


def get_panorama(pano: NaverPanorama, zoom: int = 2,
                 stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW) \
        -> Union[List[Image.Image], Image.Image]:
    """
    Downloads a panorama and returns it as PIL image.

    :param pano: The panorama.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. Defaults to 2. If 2 is unavailable, 1 will be
        downloaded instead.
    :param stitching_method: *(optional)* Whether and how the faces of the cubemap are stitched into one
        image. Defaults to ``ROW``.
    :return: A PIL image or a list of six PIL images depending on ``stitching_method``.
    """
    zoom = _validate_zoom(pano, zoom)
    if zoom == 0:
        return _get_zoom_0(pano, stitching_method)
    face_tiles, cols, rows = _generate_tile_list(pano.id, zoom)
    tile_images = _download_tiles(face_tiles)
    return _stitch_panorama(tile_images, cols, rows, stitching_method=stitching_method)


async def get_panorama_async(pano: NaverPanorama, session: ClientSession, zoom: int = 2,
                             stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW) \
        -> Union[List[Image.Image], Image.Image]:
    zoom = _validate_zoom(pano, zoom)
    if zoom == 0:
        return await _get_zoom_0_async(pano, session, stitching_method)
    face_tiles, cols, rows = _generate_tile_list(pano.id, zoom)
    tile_images = await _download_tiles_async(face_tiles, session)
    return _stitch_panorama(tile_images, cols, rows, stitching_method=stitching_method)


def download_panorama(pano: NaverPanorama, path: str, zoom: int = 2,
                      stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW,
                      pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.

    :param pano: The panorama.
    :param path: Output path.
    :param zoom: *(optional)* Image size; 0 is lowest, 2 is highest. Defaults to 2. If 2 is unavailable, 1 will be
        downloaded instead.
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


async def download_panorama_async(pano: NaverPanorama, path: str, session: ClientSession, zoom: int = 2,
                                  stitching_method: CubemapStitchingMethod = CubemapStitchingMethod.ROW,
                                  pil_args: dict = None) -> None:
    if pil_args is None:
        pil_args = {}

    output = await get_panorama_async(pano, session, zoom=zoom, stitching_method=stitching_method)
    save_cubemap_panorama(output, path, pil_args)


def get_depth(panoid: str, session: Session = None) -> np.ndarray:
    """
    Fetches the depth map of a panorama.

    :param panoid: The pano ID.
    :param session: *(optional)* A requests session.
    :return: The depth map of the faces in the order front, right, back, left, top, bottom.
    """
    depth_json = api.get_depth(panoid, session=session)
    return _parse_depth(depth_json)


async def get_depth_async(panoid: str, session: ClientSession) -> np.ndarray:
    depth_json = await api.get_depth_async(panoid, session)
    return _parse_depth(depth_json)


def _parse_depth(depth_json: dict) -> np.ndarray:
    depth = [float(n) for n in depth_json["depthmap"].split(",")]
    depth_faces = []
    for i in [0, 1, 2, 3, 5, 4]:
        # this order ^ is intentional, it reverses the top and bottom face for consistency with everything else
        depth_faces.append(np.array(depth[i * 4225:(i + 1) * 4225]).reshape(65, 65))
    return np.array(depth_faces)


def _get_zoom_0(pano: NaverPanorama, stitching_method: CubemapStitchingMethod) -> Union[List[Image.Image], Image.Image]:
    FACE_SIZE = 256
    image = get_image(f"https://panorama.pstatic.net/image/{pano.id}/512/P")
    faces = [image.crop((i*FACE_SIZE, 0, (i+1)*FACE_SIZE, FACE_SIZE)) for i in [1, 2, 3, 0, 5, 4]]
    return stitch_cubemap_faces(faces, FACE_SIZE, stitching_method)


async def _get_zoom_0_async(pano: NaverPanorama, session: ClientSession,
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


def _generate_tile_list(panoid: str, zoom: int) -> Tuple[List[List[Tile]], int, int]:
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


def _parse_neighbors(response: dict, parent_id: str) -> Neighbors:
    street = _parse_neighbor_section(response, "street", parent_id)
    other = _parse_neighbor_section(response, "air", parent_id)
    return Neighbors(street, other)


def _parse_neighbor_section(response: dict, section: str, parent_id: str) -> List[NaverPanorama]:
    panos = []
    if section in response["around"]["panoramas"]:
        for raw_pano in response["around"]["panoramas"][section][1:]:
            if raw_pano[0] == parent_id:
                continue
            elevation = raw_pano[4] * 0.01
            pano = NaverPanorama(
                id=raw_pano[0],
                lat=raw_pano[2],
                lon=raw_pano[1],
                elevation=elevation,
                camera_height=(raw_pano[3] * 0.01) - elevation)
            panos.append(pano)
    return panos


def _parse_historical(response: dict, parent_id: str) -> List[NaverPanorama]:
    panos = response["timeline"]["panoramas"][1:]
    return [NaverPanorama(
        id=pano[0],
        lat=pano[2],
        lon=pano[1],
        date=datetime.strptime(pano[3], "%Y-%m-%d %H:%M:%S.0")
    ) for pano in panos if pano[0] != parent_id]


def _parse_nearby(response: dict) -> NaverPanorama:
    feature = response["features"][0]
    elevation = feature["properties"]["land_altitude"] * 0.01
    return NaverPanorama(
        id=feature["properties"]["id"],
        lat=feature["geometry"]["coordinates"][1],
        lon=feature["geometry"]["coordinates"][0],
        heading=math.radians(feature["properties"]["camera_angle"][1]),
        date=_parse_date(feature["properties"]["photodate"]),
        description=feature["properties"]["description"],
        title=feature["properties"]["title"],
        elevation=elevation,
        camera_height=(feature["properties"]["camera_altitude"] * 0.01) - elevation
    )


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def _parse_panorama(response: dict) -> NaverPanorama:
    basic = response["basic"]
    elevation = basic["land_altitude"] * 0.01
    pano = NaverPanorama(
        id=basic["id"],
        lat=basic["latitude"],
        lon=basic["longitude"],
        heading=math.radians(basic["camera_angle"][1]),
        max_zoom=int(basic["image"]["segment"]) // 2,
        timeline_id=basic["timeline_id"],
        date=_parse_date(basic["photodate"]),
        is_latest=basic["latest"],
        description=basic["description"],
        title=basic["title"],
        panorama_type=PanoramaType(int(basic["dtl_type"])),
        elevation=elevation,
        camera_height=(basic["camera_altitude"] * 0.01) - elevation
    )

    if len(basic["image"]["overlays"]) > 1:
        pano.overlay = Overlay(
            "https://panorama.map.naver.com" + basic["image"]["overlays"][1][0],
            "https://panorama.map.naver.com" + basic["image"]["overlays"][1][1])

    pano.links = _parse_links(basic["links"])

    return pano


def _parse_links(links_json: List) -> Optional[List[Link]]:
    if len(links_json) < 2:
        return None

    links = []
    for linked_json in links_json[1:]:
        linked = NaverPanorama(
            id=linked_json[0],
            title=linked_json[1],
            lat=linked_json[5],
            lon=linked_json[4],
        )
        angle = math.radians(float(linked_json[2]))
        links.append(Link(linked, angle))
    return links
