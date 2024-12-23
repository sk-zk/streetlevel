import math
from datetime import datetime
from typing import List, Optional, Tuple

from scipy.spatial.transform import Rotation

from streetlevel.dataclasses import Link
from streetlevel.geo import get_bearing
from streetlevel.naver.panorama import Neighbors, NaverPanorama, PanoramaType, Overlay


def parse_panorama(response: dict) -> NaverPanorama:
    altitude = response["altitude"]
    heading, pitch, roll = _convert_pano_rotation(response["camera_angle"])
    pano = NaverPanorama(
        id=response["id"],
        lat=response["latitude"],
        lon=response["longitude"],
        heading=heading,
        pitch=pitch,
        roll=roll,
        max_zoom=int(response["segment"]) // 2,
        timeline_id=response["info"]["timeline_id"],
        date=_parse_date(response["info"]["photodate"]),
        is_latest=response["info"]["latest"],
        description=response["info"]["description"],
        title=response["info"]["title"],
        panorama_type=PanoramaType(int(response["dtl_type"])),
        altitude=altitude,
        has_equirect=response["proj_type"] == "equirect"
    )

    if response["overlay_type"] == "car":
        pano.overlay = Overlay(
            f"https://panorama.map.naver.com/api/v2/overlays/floor/{pano.id}",
            f"https://panorama.map.naver.com/resources/style/mask.png"
        )

    pano.links = _parse_links(response["links"], pano.lat, pano.lon)

    return pano


def _convert_pano_rotation(angle: List[float]) -> Tuple[float, float, float]:
    if angle[0] != 0:
        heading, pitch, roll = \
            Rotation.from_euler("zyx", (
                angle[2],
                angle[1],
                angle[0],
            ), True).as_euler("yxz")
        heading += math.pi
    else:
        heading = math.radians(angle[1])
        pitch = 0
        roll = 0
    return heading, pitch, roll


def parse_neighbors(response: dict, parent_id: str) -> Neighbors:
    if "street" in response["panoramas"]:
        street = _parse_neighbor_section(response["panoramas"]["street"], parent_id)
    else:
        street = None

    if "air" in response["panoramas"]:
        other = _parse_neighbor_section(response["panoramas"]["air"], parent_id)
    else:
        other = None

    return Neighbors(street, other)


def _parse_neighbor_section(section: dict, parent_id: str) -> List[NaverPanorama]:
    panos = []
    for raw_pano in section:
        if raw_pano["id"] == parent_id:
            continue
        pano = NaverPanorama(
            id=raw_pano["id"],
            lat=raw_pano["latitude"],
            lon=raw_pano["longitude"],
            altitude=raw_pano["altitude"],
            panorama_type=PanoramaType(int(raw_pano["dtl_type"])),
        )
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
    heading, pitch, roll = _convert_pano_rotation(feature["properties"]["camera_angle"])
    return NaverPanorama(
        id=feature["properties"]["id"],
        lat=feature["geometry"]["coordinates"][1],
        lon=feature["geometry"]["coordinates"][0],
        heading=heading,
        pitch=pitch,
        roll=roll,
        date=_parse_date(feature["properties"]["photodate"]),
        description=feature["properties"]["description"],
        title=feature["properties"]["title"],
        altitude=feature["properties"]["camera_altitude"] * 0.01,
        panorama_type=PanoramaType(int(feature["properties"]["type"])),
    )


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def _parse_links(links_json: List, pano_lat: float, pano_lon: float) -> Optional[List[Link]]:
    if len(links_json) < 2:
        return None

    links = []
    for link_json in links_json:
        link = NaverPanorama(
            id=link_json["id"],
            lat=link_json["latitude"],
            lon=link_json["longitude"],
            panorama_type=PanoramaType(int(link_json["dtl_type"])),
            altitude=link_json["altitude"]
        )
        angle = get_bearing(pano_lat, pano_lon, link.lat, link.lon)
        links.append(Link(link, angle))
    return links
