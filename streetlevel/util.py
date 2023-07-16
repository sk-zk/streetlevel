import asyncio
from typing import List

import aiohttp


def try_get(accessor):
    try:
        return accessor()
    except IndexError:
        return None
    except TypeError:
        return None


async def download_files_async(urls: List[str], session: aiohttp.ClientSession = None) -> List[bytes]:
    session = session if session else aiohttp.ClientSession()
    tasks = [session.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    data = []
    for response in responses:
        data.append(await response.read())
    return data
