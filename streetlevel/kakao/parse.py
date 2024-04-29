import math
from datetime import datetime
from typing import List

from streetlevel.dataclasses import Link
from streetlevel.kakao.panorama import KakaoPanorama, PanoramaType
from streetlevel.util import try_get


def parse_panoramas(response):
    return [parse_panorama(pano) for pano in response["street_view"]["streetList"]]


def parse_panorama(pano_json: dict) -> KakaoPanorama:
    pano = KakaoPanorama(
        id=pano_json["id"],
        lat=pano_json["wgsy"],
        lon=pano_json["wgsx"],
        wcongx=pano_json["wcongx"],
        wcongy=pano_json["wcongy"],
        heading=math.radians(float(pano_json["angle"])),
        image_path=pano_json["img_path"],
        # shot_date sometimes returns the time as 00:00:00, but the image url is always correct
        date=datetime.strptime(pano_json["img_path"].split("_")[-1], "%Y%m%d%H%M%S"),
        street_name=try_get(lambda: pano_json["st_name"]),
        address=try_get(lambda: pano_json["addr"]),
        street_type=try_get(lambda: pano_json["st_type"]),
        panorama_type=PanoramaType(int(pano_json["shot_tool"]))
    )

    if "past" in pano_json and pano_json["past"] is not None:
        pano.historical = [parse_panorama(past) for past in pano_json["past"]]

    if "spot" in pano_json and pano_json["past"] is not None:
        pano.links = _parse_links(pano_json["spot"])

    return pano


def _parse_links(links_json: List[dict]) -> List[Link]:
    links = []
    for linked_json in links_json:
        linked = KakaoPanorama(
            id=linked_json["id"],
            lat=linked_json["wgsy"],
            lon=linked_json["wgsx"],
            street_name=try_get(lambda: linked_json["st_name"]),
        )
        angle = math.radians(float(linked_json["pan"]))
        links.append(Link(linked, angle))
    return links
