from datetime import datetime
from enum import IntEnum
from typing import Union, Tuple

import requests
from aiohttp import ClientSession
from requests import Session

from . import api
from .auth import Authenticator
from .panorama import LookaroundPanorama, CoverageTile
from .parse import parse_coverage_tile
from .. import geo


FACE_ENDPOINT = "https://gspe72-ssl.ls.apple.com/mnn_us/"


class Face(IntEnum):
    """
    Face indices of a Look Around panorama.
    """
    BACK = 0,  #:
    LEFT = 1,  #:
    FRONT = 2,  #:
    RIGHT = 3,  #:
    TOP = 4,  #:
    BOTTOM = 5  #:


def get_coverage_tile(tile_x: int, tile_y: int, session: Session = None) -> CoverageTile:
    """
    Fetches Look Around panoramas on a specific map tile. Coordinates are in Slippy Map aka XYZ format
    at zoom level 17.

    :param tile_x: X coordinate of the tile.
    :param tile_y: Y coordinate of the tile.
    :param session: *(optional)* A requests session.
    :return: A CoverageTile object holding a list of panoramas and the last modification date of the tile.
    """
    tile, etag = api.get_coverage_tile(tile_x, tile_y, session=session)
    panos = parse_coverage_tile(tile)
    return CoverageTile(tile_x, tile_y, panos, datetime.fromtimestamp(int(etag)))


async def get_coverage_tile_async(tile_x: int, tile_y: int, session: ClientSession) -> CoverageTile:
    tile, etag = await api.get_coverage_tile_async(tile_x, tile_y, session)
    panos = parse_coverage_tile(tile)
    return CoverageTile(tile_x, tile_y, panos, datetime.fromtimestamp(int(etag)))


def get_coverage_tile_by_latlon(lat: float, lon: float, session: Session = None) -> CoverageTile:
    """
    Same as :func:`get_coverage_tile <get_coverage_tile>`, but for fetching the tile on which a point is located.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param session: *(optional)* A requests session.
    :return: A CoverageTile object holding a list of panoramas and the last modification date of the tile.
             Note that the list is not sorted - the panoramas are in the order in which they were returned by the API.
    """
    x, y = geo.wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(x, y, session=session)


async def get_coverage_tile_by_latlon_async(lat: float, lon: float, session: ClientSession) -> CoverageTile:
    x, y = geo.wgs84_to_tile_coord(lat, lon, 17)
    return await get_coverage_tile_async(x, y, session)


def get_panorama_face(pano: Union[LookaroundPanorama, Tuple[int, int]],
                      face: Union[Face, int], zoom: int,
                      auth: Authenticator, session: Session = None) -> bytes:
    """
    Fetches one face of a panorama.

    Images are in HEIC format. Since HEIC is poorly supported across the board,
    decoding the image is left to the user of the library.

    :param pano: The panorama, or its ID.
    :param face: Index of the face.
    :param zoom: The zoom level. 0 is highest, 7 is lowest.
    :param auth: An Authenticator object.
    :param session: *(optional)* A requests session.
    :return: The HEIC file containing the face, as ``bytes``.
    """
    panoid, build_id = _panoid_to_string(pano)
    url = _build_panorama_face_url(panoid, build_id, int(face), zoom, auth)
    requester = session if session else requests
    response = requester.get(url)

    if response.ok:
        return response.content
    else:
        raise Exception(str(response))


def download_panorama_face(pano: Union[LookaroundPanorama, Tuple[int, int]],
                           path: str, face: Union[Face, int], zoom: int,
                           auth: Authenticator, session: Session = None) -> None:
    """
    Downloads one face of a panorama to a file.

    :param pano: The panorama, or its ID.
    :param path: Output path.
    :param face: Index of the face.
    :param zoom: The zoom level. 0 is highest, 7 is lowest.
    :param auth: An Authenticator object.
    :param session: *(optional)* A requests session.
    """
    face_bytes = get_panorama_face(pano, face, zoom, auth, session)
    with open(path, "wb") as f:
        f.write(face_bytes)


"""
# TODO make this work. as it is, it 403s every time

async def get_panorama_face_async(pano: Union[LookaroundPanorama, Tuple[int, int]],
                                  face: Face, zoom: int,
                                  auth: Authenticator, session: ClientSession) -> bytes:
    panoid, region_id = _panoid_to_string(pano)
    url = _build_panorama_face_url(panoid, region_id, int(face), zoom, auth)
    async with session.get(url) as response:
        if response.ok:
            return await response.read()
        else:
            raise Exception(str(response))

async def download_panorama_face_async(pano: Union[LookaroundPanorama, Tuple[int, int]],
                                       path: str, face: Face, zoom: int,
                                       auth: Authenticator, session: ClientSession) -> None:
    face_bytes = await get_panorama_face_async(pano, face, zoom, auth, session)
    with open(path, "wb") as f:
        f.write(face_bytes) 
"""


def _panoid_to_string(pano: Union[LookaroundPanorama, Tuple[int, int]]) -> Tuple[str, str]:
    if isinstance(pano, LookaroundPanorama):
        panoid, build_id = str(pano.id), str(pano.build_id)
    else:
        panoid, build_id = str(pano[0]), str(pano[1])

    if len(panoid) > 20:
        raise ValueError("Pano ID must not be longer than 20 digits.")
    if len(build_id) > 10:
        raise ValueError("build_id must not be longer than 10 digits.")

    return panoid, build_id


def _build_panorama_face_url(panoid: str, build_id: str, face: int, zoom: int, auth: Authenticator) -> str:
    zoom = min(7, zoom)
    panoid_padded = panoid.zfill(20)
    panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
    panoid_url = "/".join(panoid_split)
    build_id_padded = build_id.zfill(10)
    url = FACE_ENDPOINT + f"{panoid_url}/{build_id_padded}/t/{face}/{zoom}"
    url = auth.authenticate_url(url)
    return url
