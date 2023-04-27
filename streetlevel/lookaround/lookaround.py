import math
from typing import List, Union, Tuple

import requests
from requests import Session

from streetlevel.lookaround.proto import MapTile_pb2
from .auth import Authenticator
import streetlevel.geo as geo
from .panorama import LookaroundPanorama, CoverageType

COVERAGE_TILE_ENDPOINT = "https://gspe76-ssl.ls.apple.com/api/tile?"
FACE_ENDPOINT = "https://gspe72-ssl.ls.apple.com/mnn_us/"


def get_coverage_tile_by_latlon(lat: float, lon: float, session: Session = None) -> List[LookaroundPanorama]:
    x, y = geo.wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(x, y, session=session)


def get_coverage_tile(tile_x: int, tile_y: int, session: Session = None) -> List[LookaroundPanorama]:
    tile = _get_coverage_tile_raw(tile_x, tile_y, session=session)
    panos = []
    for pano in tile.pano:
        lat, lon = _protobuf_tile_offset_to_wgs84(
            pano.location.longitude_offset,
            pano.location.latitude_offset,
            tile_x,
            tile_y)
        heading = _convert_heading(lat, lon, pano.location.heading)
        pano_obj = LookaroundPanorama(
            pano.panoid,
            tile.unknown13[pano.region_id_idx].region_id,
            lat,
            lon,
            heading,
            CoverageType(tile.unknown13[pano.region_id_idx].coverage_type),
            pano.timestamp
        )
        panos.append(pano_obj)
    return panos


def _get_coverage_tile_raw(tile_x: int, tile_y: int, session: Session = None):
    headers = {
        "maps-tile-style": "style=57&size=2&scale=0&v=0&preflight=2",
        "maps-tile-x": str(tile_x),
        "maps-tile-y": str(tile_y),
        "maps-tile-z": "17",
        "maps-auth-token": "w31CPGRO/n7BsFPh8X7kZnFG0LDj9pAuR8nTtH3xhH8=",
    }
    requester = session if session else requests
    response = requester.get(COVERAGE_TILE_ENDPOINT, headers=headers)
    tile = MapTile_pb2.MapTile()
    tile.ParseFromString(response.content)
    return tile


def get_panorama_face(pano: Union[LookaroundPanorama, Tuple[int, int]],
                      face: int, zoom: int,
                      auth: Authenticator, session: Session = None) -> bytes:
    if isinstance(pano, LookaroundPanorama):
        panoid, region_id = str(pano.id), str(pano.region_id)
    else:
        panoid, region_id = str(pano[0]), str(pano[1])

    if len(panoid) > 20:
        raise ValueError("panoid must not be longer than 20 digits.")
    if len(region_id) > 10:
        raise ValueError("region_id must not be longer than 10 digits.")
    if face > 5:
        raise ValueError("Faces range from 0 to 5 inclusive.")

    zoom = min(7, zoom)

    panoid_padded = panoid.zfill(20)
    panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
    panoid_url = "/".join(panoid_split)

    region_id_padded = region_id.zfill(10)

    url = FACE_ENDPOINT + f"{panoid_url}/{region_id_padded}/t/{face}/{zoom}"
    url = auth.authenticate_url(url)
    requester = session if session else requests
    response = requester.get(url)

    if response.ok:
        return response.content
    else:
        raise Exception(str(response))


def download_panorama_face(pano: Union[LookaroundPanorama, Tuple[int, int]],
                           path: str, face: int, zoom: int,
                           auth: Authenticator, session: Session = None) -> None:
    face_bytes = get_panorama_face(pano, face, zoom, auth, session)
    with open(path, "wb") as f:
        f.write(face_bytes)


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
