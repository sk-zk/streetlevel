import math
from datetime import datetime
from typing import List, Optional

from streetlevel.dataclasses import Link
from streetlevel.naver.panorama import Neighbors, NaverPanorama, PanoramaType, Overlay


def parse_panorama(response: dict) -> NaverPanorama:
    basic = response["basic"]
    elevation = basic["land_altitude"] * 0.01
    pano = NaverPanorama(
        id=basic["id"],
        lat=basic["latitude"],
        lon=basic["longitude"],
        heading=math.radians(basic["camera_angle"][1]),
        max_zoom=int(basic["image"]["segment"]) // 2,
        timeline_id=basic["timeline_id"],
        date=_parse_date(basic["photodate"]),
        is_latest=basic["latest"],
        description=basic["description"],
        title=basic["title"],
        panorama_type=PanoramaType(int(basic["dtl_type"])),
        elevation=elevation,
        camera_height=(basic["camera_altitude"] * 0.01) - elevation
    )

    if len(basic["image"]["overlays"]) > 1:
        pano.overlay = Overlay(
            "https://panorama.map.naver.com" + basic["image"]["overlays"][1][0],
            "https://panorama.map.naver.com" + basic["image"]["overlays"][1][1])

    pano.links = _parse_links(basic["links"])

    return pano


def parse_neighbors(response: dict, parent_id: str) -> Neighbors:
    street = _parse_neighbor_section(response, "street", parent_id)
    other = _parse_neighbor_section(response, "air", parent_id)
    return Neighbors(street, other)


def _parse_neighbor_section(response: dict, section: str, parent_id: str) -> List[NaverPanorama]:
    panos = []
    if section in response["around"]["panoramas"]:
        for raw_pano in response["around"]["panoramas"][section][1:]:
            if raw_pano[0] == parent_id:
                continue
            elevation = raw_pano[4] * 0.01
            pano = NaverPanorama(
                id=raw_pano[0],
                lat=raw_pano[2],
                lon=raw_pano[1],
                elevation=elevation,
                camera_height=(raw_pano[3] * 0.01) - elevation)
            panos.append(pano)
    return panos


def parse_historical(response: dict, parent_id: str) -> List[NaverPanorama]:
    panos = response["timeline"]["panoramas"][1:]
    return [NaverPanorama(
        id=pano[0],
        lat=pano[2],
        lon=pano[1],
        panorama_type=PanoramaType(int(pano[3])),
        date=datetime.strptime(pano[4], "%Y-%m-%d %H:%M:%S.0"),
    ) for pano in panos if pano[0] != parent_id]


def parse_nearby(response: dict) -> NaverPanorama:
    feature = response["features"][0]
    elevation = feature["properties"]["land_altitude"] * 0.01
    return NaverPanorama(
        id=feature["properties"]["id"],
        lat=feature["geometry"]["coordinates"][1],
        lon=feature["geometry"]["coordinates"][0],
        heading=math.radians(feature["properties"]["camera_angle"][1]),
        date=_parse_date(feature["properties"]["photodate"]),
        description=feature["properties"]["description"],
        title=feature["properties"]["title"],
        elevation=elevation,
        camera_height=(feature["properties"]["camera_altitude"] * 0.01) - elevation,
        panorama_type=PanoramaType(int(feature["properties"]["type"])),
    )


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def _parse_links(links_json: List) -> Optional[List[Link]]:
    if len(links_json) < 2:
        return None

    links = []
    for linked_json in links_json[1:]:
        linked = NaverPanorama(
            id=linked_json[0],
            title=linked_json[1],
            lat=linked_json[5],
            lon=linked_json[4],
        )
        angle = math.radians(float(linked_json[2]))
        links.append(Link(linked, angle))
    return links
