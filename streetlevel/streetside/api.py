from aiohttp import ClientSession
from ..util import get_json, get_json_async


def build_find_panoramas_request_url(north, west, south, east, limit):
    return f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?" \
           f"count={limit}&north={north}&south={south}&east={east}&west={west}"


def build_find_panorama_by_id_request_url(panoid):
    return f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?" \
           f"id={panoid}"


def find_panoramas(north, west, south, east, limit=50, session=None):
    return get_json(build_find_panoramas_request_url(north, west, south, east, limit), session)


async def find_panoramas_async(north, west, south, east, session: ClientSession, limit=50):
    return await get_json_async(
        build_find_panoramas_request_url(north, west, south, east, limit), session,
        # common microsoft L
        json_function_parameters={"content_type": "text/plain"})


def find_panorama_by_id(panoid, session=None):
    return get_json(build_find_panorama_by_id_request_url(panoid), session)


async def find_panorama_by_id_async(panoid, session=None):
    return await get_json_async(
        build_find_panorama_by_id_request_url(panoid), session,
        # common microsoft L
        json_function_parameters={"content_type": "text/plain"})
