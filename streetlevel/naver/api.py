import requests
from requests import Session
from aiohttp import ClientSession

from ..util import get_json, get_json_async
from streetlevel.naver.proto import Model_pb2

headers = {"Referer": "https://map.naver.com"}


def build_find_panorama_request_url(lat: float, lon: float) -> str:
    return f"https://map.naver.com/p/api/panorama/nearby/{lon}/{lat}"


def build_find_panorama_by_id_request_url(panoid: str, language: str) -> str:
    return f"https://panorama.map.naver.com/metadataV3/basic/{panoid}?lang={language}"


def build_timeline_request_url(timeline_id: str) -> str:
    return f"https://panorama.map.naver.com/metadata/timeline/{timeline_id}"


def build_around_request_url(panoid: str) -> str:
    return f"https://panorama.map.naver.com/metadataV3/around/{panoid}?lang=ko"


def build_depth_request_url(panoid: str) -> str:
    return f"https://panorama.map.naver.com/depthmap/{panoid}"


def build_model_request_url(panoid: str) -> str:
    return f"https://panorama.map.naver.com/metadataV3/model/{panoid}?modelType=v3_mesh"


def find_panorama(lat: float, lon: float, session: Session = None) -> dict:
    return get_json(build_find_panorama_request_url(lat, lon), session=session,
                    headers=headers)


async def find_panorama_async(lat: float, lon: float, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_request_url(lat, lon), session,
                                headers=headers)


def find_panorama_by_id(panoid: str, language: str, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid, language), session=session,
                    headers=headers)


async def find_panorama_by_id_async(panoid: str, language: str, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid, language), session,
                                headers=headers)


def get_historical(panoid: str, session: Session = None) -> dict:
    return get_json(build_timeline_request_url(panoid), session=session,
                    headers=headers)


async def get_historical_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_timeline_request_url(panoid), session,
                                headers=headers)


def get_neighbors(panoid: str, session: Session = None) -> dict:
    return get_json(build_around_request_url(panoid), session=session,
                    headers=headers)


async def get_neighbors_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_around_request_url(panoid), session,
                                headers=headers)


def get_depth(panoid: str, session: Session = None) -> dict:
    return get_json(build_depth_request_url(panoid), session=session,
                    headers=headers)


async def get_depth_async(panoid: str, session: ClientSession) -> dict:
    return await get_json_async(build_depth_request_url(panoid), session,
                                headers=headers)


def get_mesh(panoid: str, session: Session = None) -> Model_pb2:
    requester = session if session else requests
    response = requester.get(build_model_request_url(panoid), headers=headers)

    model = Model_pb2.Model()
    model.ParseFromString(response.content)
    return model


async def get_mesh_async(panoid: str, session: ClientSession) -> Model_pb2:
    async with session.get(build_model_request_url(panoid), headers=headers) as response:
        content = await response.read()

    model = Model_pb2.Model()
    model.ParseFromString(content)
    return model
