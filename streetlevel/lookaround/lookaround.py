from datetime import datetime
from enum import IntEnum
from typing import List, Union, Tuple

import requests
from aiohttp import ClientSession
from requests import Session

from . import api
from .auth import Authenticator
from .panorama import LookaroundPanorama, CoverageType, CameraMetadata, LensProjection, OrientedPosition
from .proto import GroundMetadataTile_pb2
from .geo import protobuf_tile_offset_to_wgs84
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


def get_coverage_tile(tile_x: int, tile_y: int, session: Session = None) -> List[LookaroundPanorama]:
    """
    Fetches Look Around panoramas on a specific map tile. Coordinates are in Slippy Map aka XYZ format
    at zoom level 17.

    :param tile_x: X coordinate of the tile.
    :param tile_y: Y coordinate of the tile.
    :param session: *(optional)* A requests session.
    :return: A list of LookaroundPanoramas. If no coverage was returned by the API, the list is empty.
    """
    tile = api.get_coverage_tile(tile_x, tile_y, session=session)
    return _parse_panos(tile, tile_x, tile_y)


async def get_coverage_tile_async(tile_x: int, tile_y: int, session: ClientSession) -> List[LookaroundPanorama]:
    tile = await api.get_coverage_tile_async(tile_x, tile_y, session)
    return _parse_panos(tile, tile_x, tile_y)


def get_coverage_tile_by_latlon(lat: float, lon: float, session: Session = None) -> List[LookaroundPanorama]:
    """
    Same as :func:`get_coverage_tile <get_coverage_tile>`, but for fetching the tile on which a point is located.

    :param lat: Latitude of the point.
    :param lon: Longitude of the point.
    :param session: *(optional)* A requests session.
    :return: A list of LookaroundPanoramas. If no coverage was returned by the API, the list is empty.
             Note that the list is not sorted - the panoramas are in the order in which they were returned by the API.
    """
    x, y = geo.wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(x, y, session=session)


async def get_coverage_tile_by_latlon_async(lat: float, lon: float, session: ClientSession) -> List[LookaroundPanorama]:
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


def _parse_panos(tile: GroundMetadataTile_pb2.GroundMetadataTile, tile_x: int, tile_y: int) -> List[LookaroundPanorama]:
    panos = []
    camera_metadatas = [_camera_metadata_to_dataclass(c) for c in tile.camera_metadata]
    for pano_pb in tile.pano:
        lat, lon = protobuf_tile_offset_to_wgs84(
            pano_pb.tile_position.x,
            pano_pb.tile_position.y,
            tile_x,
            tile_y)
        pano = LookaroundPanorama(
            id=pano_pb.panoid,
            build_id=tile.build_table[pano_pb.build_table_idx].build_id,
            lat=lat,
            lon=lon,
            coverage_type=CoverageType(tile.build_table[pano_pb.build_table_idx].coverage_type),
            date=datetime.utcfromtimestamp(pano_pb.timestamp / 1000.0),
            has_blurs=tile.build_table[pano_pb.build_table_idx].index != 0,
            raw_orientation=(pano_pb.tile_position.yaw, pano_pb.tile_position.pitch, pano_pb.tile_position.roll),
            raw_altitude=pano_pb.tile_position.altitude,
            tile=(tile_x, tile_y, 17),
            camera_metadata=[camera_metadatas[i] for i in pano_pb.camera_metadata_idx]
        )
        panos.append(pano)
    return panos


def _camera_metadata_to_dataclass(camera_metadata_pb: GroundMetadataTile_pb2.CameraMetadata):
    lens_projection_pb = camera_metadata_pb.lens_projection
    position_pb =  camera_metadata_pb.position
    return CameraMetadata(
        lens_projection=LensProjection(
            fov_s=lens_projection_pb.fov_s,
            fov_h=lens_projection_pb.fov_h,
            k2=lens_projection_pb.k2,
            k3=lens_projection_pb.k3,
            k4=lens_projection_pb.k4,
            cx=lens_projection_pb.cx,
            cy=lens_projection_pb.cy,
            lx=lens_projection_pb.lx,
            ly=lens_projection_pb.ly,
        ),
        position=OrientedPosition(
            x=position_pb.x,
            y=position_pb.y,
            z=position_pb.z,
            yaw=position_pb.yaw,
            pitch=position_pb.pitch,
            roll=position_pb.roll,
        )
    )


def _build_panorama_face_url(panoid: str, build_id: str, face: int, zoom: int, auth: Authenticator) -> str:
    zoom = min(7, zoom)
    panoid_padded = panoid.zfill(20)
    panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
    panoid_url = "/".join(panoid_split)
    build_id_padded = build_id.zfill(10)
    url = FACE_ENDPOINT + f"{panoid_url}/{build_id_padded}/t/{face}/{zoom}"
    url = auth.authenticate_url(url)
    return url
