import math
from datetime import datetime
from typing import Optional, List

from aiohttp import ClientSession
from requests import Session

from . import api
from .panorama import NaverPanorama, PanoramaType, Overlay, Neighbors


def find_panorama_by_id(panoid: str, language: str = "en",
                        neighbors: bool = True, historical: bool = True,
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
    return pano


async def find_panorama_by_id_async(panoid: str, session: ClientSession, language: str = "en",
                                    neighbors: bool = True, historical: bool = True) -> Optional[NaverPanorama]:
    response = await api.find_panorama_by_id_async(panoid, language, session)

    if "errors" in response:
        return None

    pano = _parse_panorama(response)
    if neighbors:
        pano.neighbors = await get_neighbors_async(pano.id, session)
    if historical:
        pano.historical = await get_historical_async(pano.timeline_id, session)
    return pano


def find_panorama(lat: float, lon: float, neighbors: bool = True, historical: bool = True,
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
    return pano


async def find_panorama_async(lat: float, lon: float, session: ClientSession,
                              neighbors: bool = True, historical: bool = True) -> Optional[NaverPanorama]:
    response = await api.find_panorama_async(lat, lon, session)

    if "error" in response or len(response["features"]) == 0:
        return None

    pano = _parse_nearby(response)
    if neighbors:
        pano.neighbors = await get_neighbors_async(pano.id, session)
    if historical:
        pano.historical = await get_historical_async(pano.id, session)
    return pano


def get_historical(panoid: str, session: Session = None) -> List[NaverPanorama]:
    """
    Fetches older panoramas at the location of the given panorama.

    :param panoid: The pano ID. For reasons unbeknownst to mankind, only panoramas older than the given one
        are returned, so to retrieve all available dates at this location, the ID of the most recent panorama
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


def _parse_neighbors(response: dict, parent_id: str) -> Neighbors:
    street = _parse_neighbor_section(response, "street", parent_id)
    other = _parse_neighbor_section(response, "air", parent_id)
    return Neighbors(street, other)


def _parse_neighbor_section(response: dict, section: str, parent_id: str) -> List[NaverPanorama]:
    if section in response["around"]["panoramas"]:
        return [NaverPanorama(
            id=pano[0],
            lat=pano[2],
            lon=pano[1]
        ) for pano in response["around"]["panoramas"][section][1:]
            if pano[0] != parent_id]
    else:
        return []


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
    return NaverPanorama(
        id=feature["properties"]["id"],
        lat=feature["geometry"]["coordinates"][1],
        lon=feature["geometry"]["coordinates"][0],
        heading=math.radians(feature["properties"]["camera_angle"][1]),
        date=_parse_date(feature["properties"]["photodate"]),
        description=feature["properties"]["description"],
        title=feature["properties"]["title"],
    )


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def _parse_panorama(response: dict) -> NaverPanorama:
    basic = response["basic"]
    pano = NaverPanorama(
        id=basic["id"],
        lat=basic["latitude"],
        lon=basic["longitude"],
        heading=math.radians(basic["camera_angle"][1]),
        timeline_id=basic["timeline_id"],
        date=_parse_date(basic["photodate"]),
        is_latest=basic["latest"],
        description=basic["description"],
        title=basic["title"],
        panorama_type=PanoramaType(int(basic["dtl_type"]))
    )
    if len(basic["image"]["overlays"]) > 1:
        pano.overlay = Overlay(
            "https://panorama.map.naver.com" + basic["image"]["overlays"][1][0],
            "https://panorama.map.naver.com" + basic["image"]["overlays"][1][1])
    return pano
