import math
from typing import List, Optional

from streetlevel.dataclasses import Size, Link
from streetlevel.geo import opk_to_rotation
from streetlevel.mapy.panorama import MapyPanorama


def parse_getbest_response(response: dict) -> Optional[MapyPanorama]:
    if response["status"] != 200:
        return None
    pan_info = response["result"]["panInfo"]
    return parse_pan_info_dict(pan_info)


def parse_pan_info_dict(pan_info: dict) -> MapyPanorama:
    pano = MapyPanorama(
        id=pan_info["pid"],
        lat=pan_info["mark"]["lat"],
        lon=pan_info["mark"]["lon"],
        tile_size=Size(pan_info["tileWidth"], pan_info["tileHeight"]),
        domain_prefix=pan_info["domainPrefix"],
        uri_path=pan_info["uriPath"],
        file_mask=pan_info["fileMask"],
        max_zoom=pan_info["maxZoom"],
        date=pan_info["createdAt"],
        elevation=pan_info["mark"]["alt"],
        provider=pan_info["provider"],
    )

    _parse_angles(pan_info, pano)
    pano.num_tiles = _parse_num_tiles(pan_info)

    return pano


def parse_neighbors_response(response: dict) -> List[Link]:
    if response["status"] != 200:
        return []

    panos = []
    for pan_info in response["result"]["neighbours"]:
        pano = parse_pan_info_dict(pan_info["near"])
        angle = math.radians(float(pan_info["angle"]))
        panos.append(Link(pano, angle))
    return panos


def _parse_num_tiles(pan_info: dict) -> List[Size]:
    # zoom level 0
    num_tiles = [Size(1, 1)]
    # zoom levels 1 and 2 for cyclomedia
    if "extra" in pan_info and "tileNumX" in pan_info["extra"]:
        for i in range(0, len(pan_info["extra"]["tileNumX"])):
            num = Size(int(pan_info["extra"]["tileNumX"][i]),
                       int(pan_info["extra"]["tileNumY"][i]))
            num_tiles.append(num)
    # zoom level 1 for other providers
    else:
        num_tiles.append(Size(pan_info["tileNumX"], pan_info["tileNumY"]))
    return num_tiles


def _parse_angles(pan_info: dict, pano: MapyPanorama) -> None:
    if "extra" in pan_info and "carDirection" in pan_info["extra"]:
        pano.heading = math.radians(pan_info["extra"]["carDirection"])

    pano.omega = math.radians(pan_info["omega"])
    pano.phi = math.radians(pan_info["phi"])
    pano.kappa = math.radians(pan_info["kappa"])
    heading, pitch, roll = opk_to_rotation(pano.omega, pano.phi, pano.kappa).as_euler('yxz')
    if not pano.heading:
        pano.heading = heading
    pano.pitch = pitch
    pano.roll = roll
