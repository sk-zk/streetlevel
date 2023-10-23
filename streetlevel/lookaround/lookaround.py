import math
from datetime import datetime
from enum import IntEnum
from typing import List, Union, Tuple

import requests
from aiohttp import ClientSession
from pyproj import Transformer
from requests import Session

from . import api
from .auth import Authenticator
from .panorama import LookaroundPanorama, CoverageType
from .proto import GroundMetadataTile_pb2
from .. import geo


FACE_ENDPOINT = "https://gspe72-ssl.ls.apple.com/mnn_us/"
tf_web_mercator_to_ecef = Transformer.from_crs(3857, 4978)


class Face(IntEnum):
    """
    Face indices of a Look Around panorama.
    """
    FRONT = 0,  #:
    RIGHT = 1,  #:
    BACK = 2,  #:
    LEFT = 3,  #:
    TOP = 4,  #:
    BOTTOM = 5  #:


def get_coverage_tile(tile_x: int, tile_y: int, session: Session = None) -> List[LookaroundPanorama]:
    """
    Fetches Look Around coverage on a specific map tile. Coordinates are in Slippy Map aka XYZ format
    at zoom level 17.

    :param tile_x: X coordinate of the tile.
    :param tile_y: Y coordinate of the tile.
    :param session: *(optional)* A requests session.
    :return: A list of LookaroundPanoramas. If no coverage was returned by the API, the list is empty.
    """
    tile = api.get_coverage_tile_raw(tile_x, tile_y, session=session)
    return _parse_panos(tile, tile_x, tile_y)


async def get_coverage_tile_async(tile_x: int, tile_y: int, session: ClientSession) -> List[LookaroundPanorama]:
    tile = await api.get_coverage_tile_raw_async(tile_x, tile_y, session)
    return _parse_panos(tile, tile_x, tile_y)


def get_coverage_tile_by_latlon(lat: float, lon: float, session: Session = None) -> List[LookaroundPanorama]:
    """
    Same as :func:`get_coverage_tile <get_coverage_tile>`, but for fetching the tile on which a point is located.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param session: *(optional)* A requests session.
    :return: A list of LookaroundPanoramas. If no coverage was returned by the API, the list is empty.
    """
    x, y = geo.wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(x, y, session=session)


async def get_coverage_tile_by_latlon_async(lat: float, lon: float, session: ClientSession) -> List[LookaroundPanorama]:
    x, y = geo.wgs84_to_tile_coord(lat, lon, 17)
    return await get_coverage_tile_async(x, y, session)


def get_panorama_face(pano: Union[LookaroundPanorama, Tuple[int, int]],
                      face: Face, zoom: int,
                      auth: Authenticator, session: Session = None) -> bytes:
    """
    Downloads one face of a panorama and returns it as ``bytes``.

    Images are in HEIC format. Since HEIC is a poorly supported format across the board,
    decoding the image is left to the user of the library.

    :param pano: The panorama, or its ID.
    :param face: The face.
    :param zoom: The zoom level. 0 is highest, 7 is lowest.
    :param auth: An Authenticator object.
    :param session: *(optional)* A requests session.
    :return: The HEIC file containing the face.
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
                           path: str, face: Face, zoom: int,
                           auth: Authenticator, session: Session = None) -> None:
    """
    Downloads one face of a panorama to a file.

    :param pano: The panorama, or its ID.
    :param path: Output path.
    :param face: The face.
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


def _parse_panos(tile: GroundMetadataTile_pb2.GroundMetadataTile, tile_x: int, tile_y: int) -> List[LookaroundPanorama]:
    panos = []
    for pano_pb in tile.pano:
        lat, lon = _protobuf_tile_offset_to_wgs84(
            pano_pb.tile_position.x,
            pano_pb.tile_position.y,
            tile_x,
            tile_y)
        heading = _convert_heading(lat, lon, pano_pb.tile_position.yaw)
        pano = LookaroundPanorama(
            id=pano_pb.panoid,
            build_id=tile.build_table[pano_pb.build_table_idx].build_id,
            lat=lat,
            lon=lon,
            heading=heading,
            coverage_type=CoverageType(tile.build_table[pano_pb.build_table_idx].coverage_type),
            date=datetime.utcfromtimestamp(pano_pb.timestamp / 1000.0),
            elevation=_convert_altitude(pano_pb.tile_position.altitude, lat, lon, tile_x, tile_y),
            has_blurs=tile.build_table[pano_pb.build_table_idx].index != 0,
        )
        panos.append(pano)
    return panos


def _convert_heading(lat: float, lon: float, raw_heading: int) -> float:
    """
    Converts the raw heading value to radians.
    """
    offset_factor = 1 / (16384 / 360)
    heading = (offset_factor * raw_heading) - lon
    # in the southern hemisphere, the heading also needs to be mirrored across the 90°/270° line
    if lat < 0:
        heading = -(heading - 90) + 90
    return math.radians(heading)


def _protobuf_tile_offset_to_wgs84(x_offset: int, y_offset: int, tile_x: int, tile_y: int) -> Tuple[float, float]:
    """
    Calculates the absolute position of a pano from the tile offsets returned by the API.
    :param x_offset: The X coordinate of the raw tile offset returned by the API.
    :param y_offset: The Y coordinate of the raw tile offset returned by the API.
    :param tile_x: X coordinate of the tile this pano is on, at z=17.
    :param tile_y: Y coordinate of the tile this pano is on, at z=17.
    :return: The WGS84 lat/lon of the pano.
    """
    TILE_SIZE = 256
    pano_x = tile_x + (x_offset / 64.0) / (TILE_SIZE - 1)
    pano_y = tile_y + (255 - (y_offset / 64.0)) / (TILE_SIZE - 1)
    lat, lon = geo.tile_coord_to_wgs84(pano_x, pano_y, 17)
    return lat, lon


def _build_panorama_face_url(panoid: str, build_id: str, face: int, zoom: int, auth: Authenticator) -> str:
    zoom = min(7, zoom)
    panoid_padded = panoid.zfill(20)
    panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
    panoid_url = "/".join(panoid_split)
    build_id_padded = build_id.zfill(10)
    url = FACE_ENDPOINT + f"{panoid_url}/{build_id_padded}/t/{face}/{zoom}"
    url = auth.authenticate_url(url)
    return url


def _convert_altitude(raw_altitude: int, lat: float, lon: float, tile_x: int, tile_y: int) -> float:
    """
    Converts the raw altitude returned by the API to height above MSL.

    :param raw_altitude: Raw altitude from the API.
    :param lat: WGS84 latitude of the location.
    :param lon: WGS84 longitude of the location.
    :param tile_x: X coordinate of the XYZ tile coordinates.
    :param tile_y: Y coordinate of the XYZ tile coordinates.
    :return: Height above MSL in meters.
    """
    # Adapted from _GEOOrientedPositionFromPDTilePosition in GeoServices.
    # Don't really have much of a clue what's going on here, but it seems to work
    zoom = 17
    top_left = _tile_coord_to_mercator(tile_x, tile_y, zoom)
    top_right = _tile_coord_to_mercator(tile_x + 1, tile_y, zoom)

    top_left_ecef = tf_web_mercator_to_ecef.transform(*top_left)
    top_right_ecef = tf_web_mercator_to_ecef.transform(*top_right)

    delta_x = top_left_ecef[0] - top_right_ecef[0]
    delta_y = top_left_ecef[1] - top_right_ecef[1]

    height = math.sqrt(delta_x ** 2 + delta_y ** 2) * (raw_altitude / 16383.0)
    geoid_height = geo.get_geoid_height(lat, lon)
    ortho_height = lon - geoid_height
    return height + ortho_height - lon


def _tile_coord_to_mercator(tile_x: int, tile_y: int, zoom: int) -> Tuple[float, float]:
    """
    Converts XYZ tile coordinates to Web Mercator coordinates.

    :param tile_x: X coordinate.
    :param tile_y: Y coordinate.
    :param zoom: Z coordinate.
    :return: The Web Mercator coordinate.
    """
    # Adapted from _GEOOrientedPositionFromPDTilePosition in GeoServices.
    # Don't really have much of a clue what's going on here, but it seems to work
    scale = 1 << zoom
    scale_recip = 1.0 / scale
    web_mercator_size = 40086474.44
    x = (tile_x * scale_recip - 0.5) * web_mercator_size
    y = ((scale + ~tile_y) * scale_recip - 0.5) * web_mercator_size
    return x, y
