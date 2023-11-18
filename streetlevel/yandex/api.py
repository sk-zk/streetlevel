from aiohttp import ClientSession
from requests import Session
from ..util import get_json, get_json_async


def build_find_panorama_request_url(lat: float, lon: float) -> str:
    return f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_US" \
           f"&ll={lon},{lat}&origin=userAction&provider=streetview"


def build_find_panorama_by_id_request_url(panoid: str) -> str:
    return f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_US" \
           f"&oid={panoid}&origin=userAction&provider=streetview"


def find_panorama(lat: float, lon: float, session: Session = None) -> dict:
    return get_json(build_find_panorama_request_url(lat, lon), session=session)


async def find_panorama_async(lat: float, lon: float, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_request_url(lat, lon), session)


def find_panorama_by_id(panoid: str, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid), session=session)


async def find_panorama_by_id_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid), session)
