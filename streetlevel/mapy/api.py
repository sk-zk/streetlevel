from pyfrpc import FrpcClient
from pyfrpc.asyncclient import AsyncFrpcClient

client = FrpcClient("https://pro.mapy.cz/panorpc")
async_client = AsyncFrpcClient("https://pro.mapy.cz/panorpc")

headers = {
    # Cyclomedia panos (2020+) are only returned if this header is set
    "Referer": "https://en.mapy.cz/",
}


def getbest(lat, lon, radius, options=None):
    if options is None:
        options = {}
    response = client.call("getbest",
                           args=(lon, lat, radius, options),
                           headers=headers)
    return response


async def getbest_async(lat, lon, radius, options=None):
    if options is None:
        options = {}
    response = await async_client.call("getbest",
                                       args=(lon, lat, radius, options),
                                       headers=headers)
    return response


def getneighbors(panoid):
    response = client.call("getneighbours",
                           args=(panoid,),
                           headers=headers)
    return response


async def getneighbors_async(panoid):
    response = await async_client.call("getneighbours",
                                       args=(panoid,),
                                       headers=headers)
    return response
