import asyncio

from streetlevel import ja, streetside
from aiohttp import ClientSession
import streetlevel.geo


async def main():
    #session = ClientSession()
    #pano = await ja.find_panorama_by_id_async(2514718, session)
    #...
    panos = streetside.find_panoramas(54.921613, 9.806801, 50, 100)
    ([print(p.lat, p.lon) for p in panos])

asyncio.run(main())
