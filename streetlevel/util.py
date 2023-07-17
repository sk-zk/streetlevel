import asyncio
from io import BytesIO
from typing import List
from aiohttp import ClientSession
from PIL import Image


def try_get(accessor):
    try:
        return accessor()
    except IndexError:
        return None
    except TypeError:
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


def download_tiles(tile_list):
    tiles = asyncio.run(download_files_async([t[2] for t in tile_list]))

    tile_images = {}
    for i, (x, y, url) in enumerate(tile_list):
        tile_images[(x, y)] = tiles[i]

    return tile_images


async def download_tiles_async(tile_list, session: ClientSession):
    tiles = await download_files_async([t[2] for t in tile_list], session=session)

    tile_images = {}
    for i, (x, y, url) in enumerate(tile_list):
        tile_images[(x, y)] = tiles[i]

    return tile_images


def stitch_tiles(tile_images, width, height, tile_width, tile_height):
    """
    Stitches downloaded tiles to a full image.
    """
    panorama = Image.new('RGB', (width, height))

    for x, y in tile_images:
        tile = Image.open(BytesIO(tile_images[(x, y)]))
        panorama.paste(im=tile, box=(x * tile_width, y * tile_height))
        del tile

    return panorama
