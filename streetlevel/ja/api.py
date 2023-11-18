from aiohttp import ClientSession
from requests import Session
from ..util import get_json, get_json_async


def build_find_panorama_by_id_request_url(panoid: int) -> str:
    return f"https://ja.is/kort/scene/?json=1&image_id={panoid}&lang=is"


def build_find_panorama_request_url(lat: float, lon: float, radius: int) -> str:
    return f"https://ja.is/kort/closest/?lat={lat}&lng={lon}&meters={radius}"


def find_panorama_by_id(panoid: int, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid), session)


async def find_panorama_by_id_async(panoid: int, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid), session)


def find_panorama(lat: float, lon: float, radius: int, session: Session = None) -> dict:
    return get_json(build_find_panorama_request_url(lat, lon, radius), session)


async def find_panorama_async(lat: float, lon: float, session: ClientSession, radius: int) -> dict:
    return await get_json_async(build_find_panorama_request_url(lat, lon, radius), session)
