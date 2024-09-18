import asyncio
import json
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import List, Callable, Union

import requests
from aiohttp import ClientSession
from PIL import Image
from requests import Session

from .dataclasses import Tile, Size


def download_file(url: str, path: str, session: Session = None) -> None:
    """
    Downloads a file to disk using requests.

    :param url: The URL.
    :param path: The output path.
    :param session: *(optional)* A requests session.
    """
    requester = session if session else requests
    response = requester.get(url)
    with open(path, "wb") as f:
        f.write(response.content)


async def download_file_async(url: str, path: str, session: ClientSession) -> None:
    """
    Downloads a file to disk using aiohttp.

    :param url: The URL.
    :param path: The output path.
    :param session: A ``ClientSession``.
    """
    async with session.get(url) as response:
        with open(path, "wb") as f:
            f.write(await response.read())


def get_image(url: str, session: Session = None) -> Image.Image:
    """
    Fetches an image from a URL using requests.

    :param url: The URL.
    :param session: *(optional)* A requests session.
    :return: The image as PIL Image.
    """
    requester = session if session else requests
    response = requester.get(url)
    return Image.open(BytesIO(response.content))


async def get_image_async(url: str, session: ClientSession) -> Image.Image:
    """
    Fetches an image from a URL using aiohttp.

    :param url: The URL.
    :param session: A ``ClientSession``.
    :return: The image as PIL Image.
    """
    async with session.get(url) as response:
        return Image.open(BytesIO(await response.read()))


def get_json(url: str, session: Session = None, preprocess_function: Callable = None,
             headers: dict = None) -> dict:
    """
    Fetches JSON from a URL using requests.

    :param url: The URL.
    :param session: *(optional)* A requests session.
    :param preprocess_function: *(optional)* A function to run on the text before passing it to the JSON parser.
    :param headers: *(optional)* Request headers.
    :return: The requested document as dictionary.
    """
    requester = session if session else requests
    response = requester.get(url, headers=headers)
    if preprocess_function:
        processed = preprocess_function(response.text)
        return json.loads(processed)
    else:
        return response.json()


async def get_json_async(url: str, session: ClientSession, json_function_parameters: dict = None,
                         preprocess_function: Callable = None, headers: dict = None) -> dict:
    """
    Fetches JSON from a URL using aiohttp.

    :param url: The URL.
    :param session: A ``ClientSession``.
    :param json_function_parameters: *(optional)* Parameters to pass to the ``ClientResponse.json`` function.
    :param preprocess_function: *(optional)* A function to run on the text before passing it to the JSON parser.
    :param headers: *(optional)* Request headers.
    :return: The requested document as dictionary.
    """
    if headers is None:
        headers = {}
    async with session.get(url, headers=headers) as response:
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
    """
    Downloads and stitches a tiled equirectangular panorama.

    :param width: Width of the panorama in pixels.
    :param height: Height of the panorama in pixels.
    :param tile_size: Size of one tile.
    :param tile_list: The tiles this panorama is made of.
    :return: The stitched panorama as PIL image.
    """
    tile_images = download_tiles(tile_list)
    stitched = stitch_equirectangular_tiles(tile_images, width, height, tile_size.x, tile_size.y)
    return stitched


async def get_equirectangular_panorama_async(width: int, height: int, tile_size: Size,
                                             tile_list: List[Tile],
                                             session: ClientSession) -> Image.Image:
    """
    Downloads and stitches a tiled equirectangular panorama.

    :param width: Width of the panorama in pixels.
    :param height: Height of the panorama in pixels.
    :param tile_size: Size of one tile.
    :param tile_list: The tiles this panorama is made of.
    :param session: A ``ClientSession``.
    :return: The stitched panorama as PIL image.
    """
    tile_images = await download_tiles_async(tile_list, session)
    stitched = stitch_equirectangular_tiles(tile_images, width, height, tile_size.x, tile_size.y)
    return stitched


def try_get(accessor):
    """
    QoL function for accessing an element of a nested list which may or may not exist, e.g. ``foo[1][0][2][3]``.

    :param accessor: A function which attempts to access the element, e.g. ``lambda: foo[1][0][2][3]``.
    :return: The return value of the accessor, unless an IndexError, TypeError or KeyError occurred,
     in which case the function returns None.
    """
    try:
        return accessor()
    except IndexError:
        return None
    except TypeError:
        return None
    except KeyError:
        return None


async def download_files_async(urls: List[str], session: ClientSession = None) -> List[bytes]:
    """
    Downloads multiple files to a list of ``bytes``.

    :param urls: The URLs of the files to download.
    :param session: *(optional)* A ``ClientSession``. If no session is passed, a new one will be created.
    :return: The downloaded files as ``bytes``.
    """
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
    """
    Downloads tiles to ``bytes``.

    :param tile_list: The tiles to download.
    :return: A dictionary containing the images as ``bytes`` with the key ``(x, y)``.
    """
    images = asyncio.run(download_files_async([t.url for t in tile_list]))

    images_dict = {}
    for i, tile in enumerate(tile_list):
        images_dict[(tile.x, tile.y)] = images[i]

    return images_dict


async def download_tiles_async(tile_list: List[Tile], session: ClientSession):
    """
    Downloads tiles to ``bytes``.

    :param tile_list: The tiles to download.
    :param session: A ``ClientSession``.
    :return: A dictionary containing the images as ``bytes`` with the key ``(x, y)``.
    """

    images = await download_files_async([t.url for t in tile_list], session=session)

    images_dict = {}
    for i, tile in enumerate(tile_list):
        images_dict[(tile.x, tile.y)] = images[i]

    return images_dict


def stitch_equirectangular_tiles(tile_images: dict, width: int, height: int,
                                 tile_width: int, tile_height: int) -> Image.Image:
    """
    Stitches downloaded tiles of a tiled equirectangular panorama to a full image.

    :param tile_images: The downloaded tiles.
    :param width: Width of the panorama in pixels.
    :param height: Height of the panorama in pixels.
    :param tile_width: Width of one tile in pixels.
    :param tile_height: Height of one tile in pixels.
    :return: The stitched panorama as PIL image.
    """
    panorama = Image.new('RGB', (width, height))

    for x, y in tile_images:
        tile = Image.open(BytesIO(tile_images[(x, y)]))
        panorama.paste(im=tile, box=(x * tile_width, y * tile_height))
        del tile

    return panorama


class CubemapStitchingMethod(Enum):
    """Stitching options for the faces of a cubemap."""

    NONE = 0
    """The faces are returned as a list."""

    NET = 1
    """The faces are combined into one image arranged as a net of a cube."""

    ROW = 2
    """The faces are combined into one image arranged in one row in the order front, right, back, left, top, bottom."""


def stitch_cubemap_face(face_tiles: dict, tile_size: int, cols: int, rows: int):
    """
    Stitches one face of a cubemap.

    :param face_tiles: Tiles of this face.
    :param tile_size: The side length of one tile in pixels.
    :param cols: Number of tile columns.
    :param rows: Number of tile rows.
    :return: The stitched face.
    """
    face = Image.new("RGB", (cols * tile_size, rows * tile_size))
    for row_idx in range(0, rows):
        for col_idx in range(0, cols):
            tile = Image.open(BytesIO(face_tiles[(col_idx, row_idx)]))
            face.paste(im=tile,
                       box=(col_idx * tile_size, row_idx * tile_size))
            del tile
    return face


def stitch_cubemap_faces(faces: List[Image.Image], face_size: int,
                         stitching_method: CubemapStitchingMethod) -> Union[Image.Image, List[Image.Image]]:
    """
    Stitches the six faces of a cubemap into one image.

    :param faces: A list of faces in the order front, right, back, left, top, bottom.
    :param face_size: The side length of one face of the cubemap in pixels.
    :param stitching_method: The stitching method.
    :return: A stitched image, or ``faces`` if the stitching method is ``NONE``.
    """
    if stitching_method == CubemapStitchingMethod.NONE:
        return faces
    elif stitching_method == CubemapStitchingMethod.NET:
        pano_width = 4 * face_size
        pano_height = 3 * face_size
        image = Image.new('RGB', (pano_width, pano_height))
        image.paste(im=faces[0], box=(1 * face_size, 1 * face_size))
        image.paste(im=faces[1], box=(2 * face_size, 1 * face_size))
        image.paste(im=faces[2], box=(3 * face_size, 1 * face_size))
        image.paste(im=faces[3], box=(0,             1 * face_size))
        image.paste(im=faces[4], box=(1 * face_size, 0))
        image.paste(im=faces[5], box=(1 * face_size, 2 * face_size))
        return image
    elif stitching_method == CubemapStitchingMethod.ROW:
        image = Image.new('RGB', (6 * face_size, face_size))
        for i in range(0, 6):
            image.paste(im=faces[i], box=(i * face_size, 0))
        return image
    else:
        raise ValueError("Unsupported stitching method")


def save_cubemap_panorama(pano: Union[List[Image.Image], Image.Image], path: str, pil_args: dict) -> None:
    """
    Saves a cubemap to disk.

    :param pano: A stitched cubemap, or the six faces of a cubemap.
    :param path: The output path.
    :param pil_args: *(optional)* Additional arguments for PIL's
        `Image.save <https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save>`_
        method, e.g. ``{"quality":100}``. Defaults to ``{}``.
    """
    if isinstance(pano, List):
        path_obj = Path(path)
        for idx, face in enumerate(pano):
            face_path = path_obj.parent / f"{path_obj.stem}_{idx}{path_obj.suffix}"
            face.save(face_path, **pil_args)
    else:
        pano.save(path, **pil_args)
