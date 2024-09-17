from pyfrpc import FrpcClient
from pyfrpc.asyncclient import AsyncFrpcClient
import asyncio
import atexit


class MapyApi:
    def __init__(self):
        self.client = None
        self.async_client = None
        self.headers = {
            # Cyclomedia panos (2020+) are only returned if this header is set
            "Referer": "https://en.mapy.cz/",
        }
        atexit.register(self.cleanup)

    def make_client(self):
        if self.client is None:
            self.client = FrpcClient("https://pro.mapy.cz/panorpc")

    def make_async_client(self):
        if self.async_client is None:
            self.async_client = AsyncFrpcClient("https://pro.mapy.cz/panorpc")

    def cleanup(self):
        try:
            loop = asyncio.get_event_loop()
            asyncio.create_task(self._cleanup())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._cleanup())

    async def _cleanup(self):
        if self.async_client is not None:
            await self.async_client.close()
            self.async_client = None

    def getbest(self, lat, lon, radius, options=None):
        self.make_client()
        if options is None:
            options = {}
        response = self.client.call("getbest",
                                    args=(lon, lat, radius, options),
                                    headers=self.headers)
        return response

    async def getbest_async(self, lat, lon, radius, options=None):
        self.make_async_client()
        if options is None:
            options = {}
        response = await self.async_client.call("getbest",
                                                args=(lon, lat, radius, options),
                                                headers=self.headers)
        return response

    def detail(self, panoid: int):
        self.make_client()
        response = self.client.call("detail", args=[panoid], headers=self.headers)
        return response

    async def detail_async(self, panoid: int):
        self.make_async_client()
        response = await self.async_client.call("detail", args=[panoid], headers=self.headers)
        return response

    def getneighbours(self, panoid: int, options=None):
        self.make_client()
        if options is None:
            options = {}
        response = self.client.call("getneighbours",
                                    args=(panoid, options),
                                    headers=self.headers)
        return response

    async def getneighbours_async(self, panoid: int, options):
        self.make_async_client()
        if options is None:
            options = {}
        response = await self.async_client.call("getneighbours",
                                                args=(panoid, options),
                                                headers=self.headers)
        return response
