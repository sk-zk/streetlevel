import requests
from aiohttp import ClientSession
from requests import Session


def build_find_panorama_by_id_request_url(panoid: int) -> str:
    return f"https://rv.map.kakao.com/roadview-search/v2/node/{panoid}?SERVICE=glpano"


def find_panorama_by_id_raw(panoid: int, session: Session = None) -> dict:
    url = build_find_panorama_by_id_request_url(panoid)

    requester = session if session else requests
    response = requester.get(url)

    return response.json()


async def find_panorama_by_id_raw_async(panoid: int, session: ClientSession) -> dict:
    url = build_find_panorama_by_id_request_url(panoid)

    async with session.get(url) as response:
        pano = await response.json()

    return pano


def build_find_panoramas_request_url(lat: float, lon: float, radius: int, limit: int) -> str:
    return f"https://rv.map.kakao.com/roadview-search/v2/nodes?" \
           f"PX={lon}&PY={lat}&RAD={radius}&PAGE_SIZE={limit}&INPUT=wgs&TYPE=w&SERVICE=glpano"


def find_panoramas_raw(lat: float, lon: float, radius: int, limit: int, session: Session = None) -> dict:
    url = build_find_panoramas_request_url(lat, lon, radius, limit)

    requester = session if session else requests
    response = requester.get(url)

    return response.json()


async def find_panoramas_raw_async(lat: float, lon: float, session: ClientSession, radius: int, limit: int) -> dict:
    url = build_find_panoramas_request_url(lat, lon, radius, limit)

    async with session.get(url) as response:
        pano = await response.json()

    return pano
