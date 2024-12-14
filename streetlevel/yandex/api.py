from aiohttp import ClientSession
from requests import Session
from ..util import get_json, get_json_async

_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
              "Chrome/131.0.0.0 Safari/537.36"


def build_find_panorama_request_url(lat: float, lon: float) -> str:
    return f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_US" \
           f"&ll={lon},{lat}&origin=userAction&provider=streetview"


def build_find_panorama_by_id_request_url(panoid: str) -> str:
    return f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_US" \
           f"&oid={panoid}&origin=userAction&provider=streetview"


def find_panorama(lat: float, lon: float, session: Session = None) -> dict:
    return get_json(build_find_panorama_request_url(lat, lon), session=session,
                    headers={"User-Agent": _user_agent})


async def find_panorama_async(lat: float, lon: float, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_request_url(lat, lon), session,
                                headers={"User-Agent": _user_agent})


def find_panorama_by_id(panoid: str, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid), session=session,
                    headers={"User-Agent": _user_agent})


async def find_panorama_by_id_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid), session,
                                headers={"User-Agent": _user_agent})
