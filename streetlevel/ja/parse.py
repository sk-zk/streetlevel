import math
from typing import List, Optional

from streetlevel.ja.panorama import JaPanorama, Address, StreetLabel, CaptureDate
from streetlevel.util import try_get


def parse_panorama_radius_response(pano_dict: dict) -> Optional[JaPanorama]:
    if "message" in pano_dict:
        return None

    return JaPanorama(
        id=pano_dict["id"],
        lat=pano_dict["lat"],
        lon=pano_dict["lng"],
        heading=math.radians(pano_dict["image_heading"]),
    )


def parse_panorama_id_response(pano_dict: dict) -> JaPanorama:
    address = try_get(lambda: pano_dict["streets"]["nearestAddress"])
    if address:
        address = Address(*address.values())

    return JaPanorama(
        id=pano_dict["image"]["id"],
        lat=pano_dict["image"]["lat"],
        lon=pano_dict["image"]["lng"],
        heading=math.radians(pano_dict["image"]["heading"]),
        date=_parse_date(pano_dict["image"]["month"]),
        pano_url="https:" + pano_dict["image"]["pano_url"],
        blur_key=pano_dict["image"]["blur_key"],
        street_names=_parse_streets(pano_dict["streets"]),
        address=address,
        neighbors=_parse_hotspots(pano_dict["hotspots"]),
    )


def _parse_streets(streets: dict) -> List[StreetLabel]:
    main = StreetLabel(name=streets["street"]["name"],
                       angles=[math.radians(a) for a in streets["street"]["azimuths"]])
    connections = []
    for connection_dict in streets["connections"]:
        connection = StreetLabel(name=connection_dict["name"],
                                 angles=[math.radians(connection_dict["angle"])],
                                 distance=connection_dict["distance"])
        connections.append(connection)

    return [main] + connections


def _parse_hotspots(hotspots: list) -> List[JaPanorama]:
    neighbors = []
    for hotspot in hotspots:
        neighbors.append(JaPanorama(
            id=hotspot["image"]["id"],
            lat=hotspot["image"]["lat"],
            lon=hotspot["image"]["lng"],
            heading=math.radians(hotspot["image"]["heading"]),
            date=_parse_date(hotspot["image"]["month"]),
            pano_url="https:" + hotspot["image"]["pano_url"],
            blur_key=hotspot["image"]["blur_key"],
        ))
    return neighbors


def _parse_date(date_str: str) -> CaptureDate:
    year, month = date_str.split("-")
    date = CaptureDate(int(year), int(month))
    return date

