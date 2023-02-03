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


async def download_files_async(urls: List[str]) -> List[bytes]:
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        data = []
        for response in responses:
            data.append(await response.read())
        return data
