import os
from datetime import datetime
from io import BytesIO
import math
import numpy as np
from PIL import Image
import requests
from .panorama import StreetsidePanorama


TILE_SIZE = 256


def to_base4(n):
    return np.base_repr(n, 4)


def from_base4(n):
    return int(n, 4)


def find_panoramas(north, west, south, east, limit=50):
    """
    Returns panoramas within a bounding box (I think).
    """
    url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?count={limit}&north={north}&south={south}&east={east}&west={west}"
    response = requests.get(url)
    response_panos = response.json()

    panos = []
    for pano in response_panos[1:]:  # first object is elapsed time
        # todo: parse ro, pi, he, bl, ml, nbn, pbn, ad fields
        pano_obj = StreetsidePanorama(pano["id"], pano["la"], pano["lo"])
        if "cd" in pano:
            # as it turns out, months/years without leading zeros
            # don't have a cross-platform format code in strptime.
            # wanna guess what kind of dates bing returns?
            datestr = pano["cd"]
            datestr = datestr.split("/")
            datestr[0] = datestr[0].rjust(2, "0")
            datestr[1] = datestr[1].rjust(2, "0")
            datestr = "/".join(datestr)
            pano_obj.date = datetime.strptime(datestr, "%m/%d/%Y %I:%M:%S %p")
        if "ne" in pano:
            pano_obj.next = pano["ne"]
        if "pr" in pano:
            pano_obj.next = pano["pr"]
        if "al" in pano:
            pano_obj.altitude = pano["al"]
        panos.append(pano_obj)
    return panos


def download_panorama(panoid, directory, zoom=3):
    """
    Downloads a panorama to the given directory.
    """
    pano = get_panorama(panoid, zoom)
    pano.save(os.path.join(directory, f"{panoid}.jpg"))


def get_panorama(panoid, zoom=3):
    """
    Downloads a panorama as PIL image.
    """
    faces = _generate_tile_list(panoid, zoom)
    _download_tiles(faces)
    return _stitch_panorama(faces)


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
    session = requests.Session()
    for face_id, face in faces.items():
        for tile in face:
            url = tile["url"]
            response = session.get(url)
            tile["image"] = response.content


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


def _stitch_panorama(faces):
    """
    Stitches downloaded tiles into a full image.
    """
    full_tile_size = int(math.sqrt(len(faces[1]))) * TILE_SIZE
    pano_width = 4 * full_tile_size
    pano_height = 3 * full_tile_size
    panorama = Image.new('RGB', (pano_width, pano_height))
    stitched_faces = []
    if len(faces[1]) == 1:
        for i in range(0, 6):
            stitched_faces.append(Image.open(BytesIO(faces[i][0]["image"])))
    else:
        for i in range(0, 6):
            stitched_faces.append(_stitch_face(faces[i]))
    panorama.paste(im=stitched_faces[0], box=(1 * full_tile_size, 1 * full_tile_size))
    panorama.paste(im=stitched_faces[1], box=(2 * full_tile_size, 1 * full_tile_size))
    panorama.paste(im=stitched_faces[2], box=(3 * full_tile_size, 1 * full_tile_size))
    panorama.paste(im=stitched_faces[3], box=(0, 1 * full_tile_size))
    panorama.paste(im=stitched_faces[4], box=(1 * full_tile_size, 0))
    panorama.paste(im=stitched_faces[5], box=(1 * full_tile_size, 2 * full_tile_size))
    return panorama

