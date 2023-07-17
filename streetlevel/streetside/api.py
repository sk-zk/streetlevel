import requests
from aiohttp import ClientSession


def find_panoramas_raw(north, west, south, east, limit=50, session=None):
    url = build_find_panoramas_request_url(north, west, south, east, limit)

    requester = session if session else requests
    response = requester.get(url)

    panos = response.json()
    return panos


async def find_panoramas_raw_async(north, west, south, east, session: ClientSession, limit=50):
    url = build_find_panoramas_request_url(north, west, south, east, limit)

    async with session.get(url) as response:
        panos = await response.json(
            # common microsoft L
            content_type="text/plain")

    return panos


def find_panorama_by_id_raw(panoid, session=None):
    url = build_find_panorama_by_id_request_url(panoid)

    requester = session if session else requests
    response = requester.get(url)

    pano = response.json()
    return pano


async def find_panorama_by_id_raw_async(panoid, session=None):
    url = build_find_panorama_by_id_request_url(panoid)

    async with session.get(url) as response:
        pano = await response.json(
            # common microsoft L
            content_type="text/plain")

    return pano


def build_find_panoramas_request_url(north, west, south, east, limit):
    return f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?" \
           f"count={limit}&north={north}&south={south}&east={east}&west={west}"


def build_find_panorama_by_id_request_url(panoid):
    return f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?" \
           f"id={panoid}"
