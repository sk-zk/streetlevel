import asyncio
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image
import requests
from requests import Session

from .panorama import StreetsidePanorama
from streetlevel.geo import *
from ..util import download_files_async

TILE_SIZE = 256


def to_base4(n: int) -> str:
    return np.base_repr(n, 4)


def from_base4(n: str) -> int:
    return int(n, 4)


def find_panoramas_in_bbox(north: float, west: float, south: float, east: float,
                           limit: int = 50, session: Session = None) -> List[StreetsidePanorama]:
    """
    Retrieves panoramas within a bounding box.
    """
    response = _find_panoramas_raw(north, west, south, east, limit, session)

    panos = []
    for pano in response[1:]:  # first object is elapsed time
        # TODO: parse bl, ml, nbn, pbn, ad fields

        # as it turns out, months/days without leading zeros
        # don't have a cross-platform format code in strptime.
        # wanna guess what kind of dates bing returns?
        datestr = pano["cd"]
        datestr = datestr.split("/")
        datestr[0] = datestr[0].rjust(2, "0")
        datestr[1] = datestr[1].rjust(2, "0")
        datestr = "/".join(datestr)
        date = datetime.strptime(datestr, "%m/%d/%Y %I:%M:%S %p")

        pano_obj = StreetsidePanorama(
            id=pano["id"],
            lat=pano["la"],
            lon=pano["lo"],
            date=date,
            next=pano["ne"] if "ne" in pano else None,
            previous=pano["pr"] if "pr" in pano else None,
            elevation=pano["al"] if "al" in pano else None,
            heading=math.radians(pano["he"]) if "he" in pano else None,
            pitch=math.radians(pano["pi"]) if "pi" in pano else None,
            roll=math.radians(pano["ro"]) if "ro" in pano else None,
        )
        panos.append(pano_obj)
    return panos


def _find_panoramas_raw(north, west, south, east, limit=50, session=None):
    url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?" \
          f"count={limit}&north={north}&south={south}&east={east}&west={west}"
    if session is None:
        response = requests.get(url)
    else:
        response = session.get(url)
    panos = response.json()
    return panos


def find_panoramas(lat: float, lon: float, radius: float = 25,
                   limit: int = 50, session: Session = None) -> List[StreetsidePanorama]:
    """
    Retrieves panoramas within a square around a point.
    """
    top_left, bottom_right = create_bounding_box_around_point(lat, lon, radius)
    return find_panoramas_in_bbox(
        top_left[1], top_left[0],
        bottom_right[1], bottom_right[0],
        limit=limit, session=session)


def download_panorama(panoid: int, path: str, zoom: int = 3, single_image: bool = True, pil_args: dict = None) -> None:
    """
    Downloads a panorama to a file.
    """
    if pil_args is None:
        pil_args = {}

    if single_image:
        pano = get_panorama(panoid, zoom=zoom, single_image=single_image)
        pano.save(path, **pil_args)
    else:
        faces = get_panorama(panoid, zoom=zoom, single_image=single_image)
        path = Path(path)
        for idx, face in enumerate(faces):
            face_path = path.parent / f"{path.stem}_{idx}{path.suffix}"
            face.save(face_path, **pil_args)


def get_panorama(panoid: int, zoom: int = 3, single_image: bool = True) -> List[Image.Image] | Image.Image:
    """
    Downloads a panorama as PIL image.
    """
    faces = _generate_tile_list(panoid, zoom)
    _download_tiles(faces)
    return _stitch_panorama(faces, single_image=single_image)


def _generate_tile_list(panoid, zoom):
    """
    Generates a list of a panorama's tiles.
    Returns a list of faces and its tiles.
    """
    if zoom > 3:
        raise ValueError("Zoom can't be greater than 3")
    panoid_base4 = to_base4(panoid).rjust(16, "0")
    subdivs = pow(4, zoom)
    faces = {}
    for face_id in range(0, 6):
        face_id_base4 = to_base4(face_id + 1).rjust(2, "0")
        face_tiles = []
        for subdiv in range(0, subdivs):
            if zoom < 1:
                subdiv_base4 = ""
            else:
                subdiv_base4 = to_base4(subdiv).rjust(zoom, "0")
            tile_key = f"{face_id_base4}{subdiv_base4}"
            url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/hs{panoid_base4}{tile_key}.jpg?g=0"
            face_tiles.append({"face": face_id_base4, "subdiv": subdiv, "url": url})
        faces[face_id] = face_tiles
    return faces


def _download_tiles(faces):
    """
    Downloads the tiles of a panorama.
    """
    for face_id, face in faces.items():
        tiles = asyncio.run(download_files_async([tile["url"] for tile in face]))
        for idx, tile in enumerate(face):
            tile["image"] = tiles[idx]


def _stitch_four(face):
    """
    Stitches four consecutive individual tiles.
    """
    sub_tile = Image.new('RGB', (TILE_SIZE * 2, TILE_SIZE * 2))
    for idx, tile in enumerate(face[0:4]):
        tile_img = Image.open(BytesIO(tile["image"]))
        x = idx % 2
        y = idx // 2
        sub_tile.paste(im=tile_img, box=(x * TILE_SIZE, y * TILE_SIZE))
    return sub_tile


split_list = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]


def _stitch_face(face):
    """
    Stitches one face of a panorama.
    """
    if len(face) <= 4:
        return _stitch_four(face)
    else:
        grid_size = int(math.sqrt(len(face)))
        stitched_tile_size = (grid_size // 2) * TILE_SIZE
        tile = Image.new('RGB', (stitched_tile_size * 2, stitched_tile_size * 2))
        split = split_list(face, len(face) // 4)
        tile.paste(im=_stitch_face(split[0]), box=(0, 0))
        tile.paste(im=_stitch_face(split[1]), box=(stitched_tile_size, 0))
        tile.paste(im=_stitch_face(split[2]), box=(0, stitched_tile_size))
        tile.paste(im=_stitch_face(split[3]), box=(stitched_tile_size, stitched_tile_size))
        return tile


def _stitch_panorama(faces, single_image: bool = True) -> List[Image.Image] | Image.Image:
    """
    Stitches downloaded tiles into full faces or one full image.
    """
    full_tile_size = int(math.sqrt(len(faces[1]))) * TILE_SIZE

    stitched_faces = []
    if len(faces[1]) == 1:
        for i in range(0, 6):
            stitched_faces.append(Image.open(BytesIO(faces[i][0]["image"])))
    else:
        for i in range(0, 6):
            stitched_faces.append(_stitch_face(faces[i]))

    if not single_image:
        return stitched_faces
    else:
        pano_width = 4 * full_tile_size
        pano_height = 3 * full_tile_size
        image = Image.new('RGB', (pano_width, pano_height))

        image.paste(im=stitched_faces[0], box=(1 * full_tile_size, 1 * full_tile_size))
        image.paste(im=stitched_faces[1], box=(2 * full_tile_size, 1 * full_tile_size))
        image.paste(im=stitched_faces[2], box=(3 * full_tile_size, 1 * full_tile_size))
        image.paste(im=stitched_faces[3], box=(0,                  1 * full_tile_size))
        image.paste(im=stitched_faces[4], box=(1 * full_tile_size, 0))
        image.paste(im=stitched_faces[5], box=(1 * full_tile_size, 2 * full_tile_size))
        return image
