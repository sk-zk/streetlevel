import asyncio
from io import BytesIO
from typing import List
from aiohttp import ClientSession
from PIL import Image

from .dataclasses import Tile


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
