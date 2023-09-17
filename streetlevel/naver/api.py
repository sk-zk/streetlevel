from requests import Session
from aiohttp import ClientSession

from ..util import get_json, get_json_async


def build_find_panorama_request_url(lat: float, lon: float) -> str:
    return f"https://map.naver.com/p/api/panorama/nearby/{lon}/{lat}"


def build_find_panorama_by_id_request_url(panoid: str, language: str) -> str:
    return f"https://panorama.map.naver.com/metadata/basic/{panoid}?lang={language}&version=2.1.0"


def build_timeline_request_url(panoid: str) -> str:
    return f"https://panorama.map.naver.com/metadata/timeline/{panoid}"


def build_around_request_url(panoid: str) -> str:
    return f"https://panorama.map.naver.com/metadata/around/{panoid}?lang=ko"


def build_depth_request_url(panoid: str) -> str:
    return f"https://panorama.map.naver.com/depthmap/{panoid}"


def find_panorama(lat: float, lon: float, session: Session = None) -> dict:
    return get_json(build_find_panorama_request_url(lat, lon), session=session)


async def find_panorama_async(lat: float, lon: float, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_request_url(lat, lon), session)


def find_panorama_by_id(panoid: str, language: str, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid, language), session=session)


async def find_panorama_by_id_async(panoid: str, language: str, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid, language), session)


def get_historical(panoid: str, session: Session = None) -> dict:
    return get_json(build_timeline_request_url(panoid), session=session)


async def get_historical_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_timeline_request_url(panoid), session)


def get_neighbors(panoid: str, session: Session = None) -> dict:
    return get_json(build_around_request_url(panoid), session=session)


async def get_neighbors_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_around_request_url(panoid), session)


def get_depth(panoid: str, session: Session = None) -> dict:
    return get_json(build_depth_request_url(panoid), session=session)


async def get_depth_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_depth_request_url(panoid), session)
