from aiohttp import ClientSession
from requests import Session
from ..util import get_json, get_json_async


def build_find_panorama_request_url(x: float, y: float) -> str:
    return f"https://mapsv0.bdimg.com/?qt=qsdata&x={x}&y={y}&action=1"


def build_find_panorama_by_id_request_url(panoid: str) -> str:
    return f"https://mapsv0.bdimg.com/?qt=sdata&pc=1&sid={panoid}"


def build_get_inter_metadata_url(iid: str) -> str:
    return f"https://mapsv0.bdimg.com/?qt=idata&iid={iid}"


def find_panorama(x: float, y: float, session: Session = None) -> dict:
    return get_json(build_find_panorama_request_url(x, y), session=session)


async def find_panorama_async(x: float, y: float, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_request_url(x, y), session)


def find_panorama_by_id(panoid: str, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid), session=session)


async def find_panorama_by_id_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid), session)


def get_inter_metadata(iid: str, session: Session = None) -> dict:
    return get_json(build_get_inter_metadata_url(iid), session=session)


async def get_inter_metadata_async(iid: str, session: ClientSession) -> dict:
    return await get_json_async(build_get_inter_metadata_url(iid), session=session)
