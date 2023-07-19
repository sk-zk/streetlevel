import math
from datetime import datetime
from enum import IntEnum
from typing import List, Union, Tuple

import requests
from requests import Session

from . import api
from .auth import Authenticator
import streetlevel.geo as geo
from .panorama import LookaroundPanorama, CoverageType

FACE_ENDPOINT = "https://gspe72-ssl.ls.apple.com/mnn_us/"


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


def get_panorama_face(pano: Union[LookaroundPanorama, Tuple[int, int]],
                      face: Face, zoom: int,
                      auth: Authenticator, session: Session = None) -> bytes:
    """
    Downloads one face of a panorama and returns it as ``bytes``.

    Images are in HEIC format. Since HEIC is a poorly supported format across the board,
    decoding the image is left to the user of the library.

    :param pano: The panorama, or its ID.
    :param face: The face.
    :param zoom: The zoom level. 0 is highest, 7 is lowest. Defaults to 0.
    :param auth: An Authenticator object.
    :param session: *(optional)* A requests session.
    :return: The HEIC file containing the face.
    """
    panoid, region_id = _panoid_to_string(pano)
    url = _build_panorama_face_url(panoid, region_id, int(face), zoom, auth)
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
    :param zoom: The zoom level. 0 is highest, 7 is lowest. Defaults to 0.
    :param auth: An Authenticator object.
    :param session: *(optional)* A requests session.
    """
    face_bytes = get_panorama_face(pano, face, zoom, auth, session)
    with open(path, "wb") as f:
        f.write(face_bytes)


def _panoid_to_string(pano):
    if isinstance(pano, LookaroundPanorama):
        panoid, region_id = str(pano.id), str(pano.region_id)
    else:
        panoid, region_id = str(pano[0]), str(pano[1])

    if len(panoid) > 20:
        raise ValueError("panoid must not be longer than 20 digits.")
    if len(region_id) > 10:
        raise ValueError("region_id must not be longer than 10 digits.")

    return panoid, region_id


def _parse_panos(tile, tile_x, tile_y):
    panos = []
    for raw_pano in tile.pano:
        lat, lon = _protobuf_tile_offset_to_wgs84(
            raw_pano.location.longitude_offset,
            raw_pano.location.latitude_offset,
            tile_x,
            tile_y)
        heading = _convert_heading(lat, lon, raw_pano.location.heading)
        pano = LookaroundPanorama(
            raw_pano.panoid,
            tile.unknown13[raw_pano.region_id_idx].region_id,
            lat,
            lon,
            heading,
            CoverageType(tile.unknown13[raw_pano.region_id_idx].coverage_type),
            datetime.utcfromtimestamp(raw_pano.timestamp / 1000.0)
        )
        panos.append(pano)
    return panos


def _convert_heading(lat: float, lon: float, raw_heading: int) -> float:
    """
    Converts the raw heading value to radians.
    """
    offset_factor = 1/(16384/360)
    heading = (offset_factor * raw_heading) - lon
    # in the southern hemisphere, the heading also needs to be mirrored across the 90°/270° line
    if lat < 0:
        heading = -(heading - 90) + 90
    return math.radians(heading)


def _protobuf_tile_offset_to_wgs84(x_offset: int, y_offset: int, tile_x: int, tile_y: int) -> (float, float):
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


def _build_panorama_face_url(panoid: str, region_id: str, face: int, zoom: int, auth: Authenticator):
    zoom = min(7, zoom)
    panoid_padded = panoid.zfill(20)
    panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
    panoid_url = "/".join(panoid_split)
    region_id_padded = region_id.zfill(10)
    url = FACE_ENDPOINT + f"{panoid_url}/{region_id_padded}/t/{face}/{zoom}"
    url = auth.authenticate_url(url)
    return url
