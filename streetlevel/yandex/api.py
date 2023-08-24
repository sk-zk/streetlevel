import requests
from aiohttp import ClientSession
from requests import Session


def build_find_panorama_request_url(lat: float, lon: float) -> str:
    return f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_US" \
           f"&ll={lon},{lat}&origin=userAction&provider=streetview"


def find_panorama_raw(lat: float, lon: float, session: Session = None) -> dict:
    url = build_find_panorama_request_url(lat, lon)

    requester = session if session else requests
    response = requester.get(url)

    pano = response.json()
    return pano


async def find_panorama_raw_async(lat: float, lon: float, session: ClientSession) -> dict:
    url = build_find_panorama_request_url(lat, lon)

    async with session.get(url) as response:
        pano = await response.json()

    return pano


def build_find_panorama_by_id_request_url(panoid: str) -> str:
    return f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_US" \
           f"&oid={panoid}&origin=userAction&provider=streetview"


def find_panorama_by_id_raw(panoid: str, session: Session = None) -> dict:
    url = build_find_panorama_by_id_request_url(panoid)

    requester = session if session else requests
    response = requester.get(url)

    pano = response.json()
    return pano


async def find_panorama_by_id_raw_async(panoid: str, session: ClientSession) -> dict:
    url = build_find_panorama_by_id_request_url(panoid)

    async with session.get(url) as response:
        pano = await response.json()

    return pano
