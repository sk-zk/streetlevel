import asyncio
import json
from io import BytesIO
from typing import List, Callable

import requests
from aiohttp import ClientSession
from PIL import Image
from requests import Session

from .dataclasses import Tile, Size


def download_file(url: str, path: str, session: Session = None) -> None:
    requester = session if session else requests
    response = requester.get(url)
    with open(path, "wb") as f:
        f.write(response.content)


async def download_file_async(url: str, path: str, session: ClientSession) -> None:
    async with session.get(url) as response:
        with open(path, "wb") as f:
            f.write(await response.read())


def get_image(url: str, session: Session = None) -> Image.Image:
    """
    Fetches an image from a URL.

    :param url: The URL.
    :param session: *(optional)* A requests session.
    :return: The image as PIL Image.
    """
    requester = session if session else requests
    response = requester.get(url)
    return Image.open(BytesIO(response.content))


async def get_image_async(url: str, session: ClientSession) -> Image.Image:
    async with session.get(url) as response:
        return Image.open(BytesIO(await response.read()))


def get_json(url: str, session: Session = None, preprocess_function: Callable = None) -> dict:
    """
    Fetches JSON from a URL.

    :param url: The URL.
    :param session: *(optional)* A requests session.
    :param preprocess_function: *(optional)* A function to run on the text before passing it to the JSON parser.
    :return: The requested document as dict.
    """
    requester = session if session else requests
    response = requester.get(url)
    if preprocess_function:
        processed = preprocess_function(response.text)
        return json.loads(processed)
    else:
        return response.json()


async def get_json_async(url: str, session: ClientSession, json_function_parameters: dict = None,
                         preprocess_function: Callable = None) -> dict:
    """
    Fetches JSON from a URL.

    :param url: The URL.
    :param session: A ClientSession.
    :param json_function_parameters: *(optional)* Parameters to pass to the ``ClientResponse.json()`` function.
    :param preprocess_function: *(optional)* A function to run on the text before passing it to the JSON parser.
    :return: The requested document as dict.
    """
    async with session.get(url) as response:
        if preprocess_function:
            text = await response.text()
            processed = preprocess_function(text)
            return json.loads(processed)
        else:
            if json_function_parameters:
                return await response.json(**json_function_parameters)
            return await response.json()


def get_equirectangular_panorama(width: int, height: int, tile_size: Size,
                                 tile_list: List[Tile]) -> Image.Image:
    tile_images = download_tiles(tile_list)
    stitched = stitch_tiles(tile_images, width, height, tile_size.x, tile_size.y)
    return stitched


async def get_equirectangular_panorama_async(width: int, height: int, tile_size: Size,
                                             tile_list: List[Tile],
                                             session: ClientSession) -> Image.Image:
    tile_images = await download_tiles_async(tile_list, session)
    stitched = stitch_tiles(tile_images, width, height, tile_size.x, tile_size.y)
    return stitched


def try_get(accessor):
    try:
        return accessor()
    except IndexError:
        return None
    except TypeError:
        return None
    except KeyError:
        return None


async def download_files_async(urls: List[str], session: ClientSession = None) -> List[bytes]:
    close_session = session is None
    session = session if session else ClientSession()

    tasks = [session.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    data = []
    for response in responses:
        data.append(await response.read())

    if close_session:
        await session.close()

    return data


def download_tiles(tile_list: List[Tile]) -> dict:
    images = asyncio.run(download_files_async([t.url for t in tile_list]))

    images_dict = {}
    for i, tile in enumerate(tile_list):
        images_dict[(tile.x, tile.y)] = images[i]

    return images_dict


async def download_tiles_async(tile_list: List[Tile], session: ClientSession):
    images = await download_files_async([t.url for t in tile_list], session=session)

    images_dict = {}
    for i, tile in enumerate(tile_list):
        images_dict[(tile.x, tile.y)] = images[i]

    return images_dict


def stitch_tiles(tile_images: dict, width: int, height: int, tile_width: int, tile_height: int) -> Image.Image:
    """
    Stitches downloaded tiles to a full image.
    """
    panorama = Image.new('RGB', (width, height))

    for x, y in tile_images:
        tile = Image.open(BytesIO(tile_images[(x, y)]))
        panorama.paste(im=tile, box=(x * tile_width, y * tile_height))
        del tile

    return panorama
