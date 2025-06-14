import math
import re
from datetime import datetime, timezone
from typing import List, Tuple, Optional

from streetlevel.dataclasses import Size, Link
from streetlevel.util import try_get
from streetlevel.yandex.panorama import YandexPanorama, Place, Address, Marker


def parse_panorama_response(response: dict) -> Optional[YandexPanorama]:
    if response["status"] == "error":
        return None
    return parse_panorama(response["data"])


def parse_panorama(pano_dict: dict) -> YandexPanorama:
    data = pano_dict["Data"]
    annotation = pano_dict["Annotation"]
    panoid = data["panoramaId"]

    addresses, other_markers = _parse_markers(annotation["Markers"])

    return YandexPanorama(
        id=panoid,
        lat=float(data["Point"]["coordinates"][1]),
        lon=float(data["Point"]["coordinates"][0]),

        heading=math.radians(float(data["EquirectangularProjection"]["Origin"][0])),

        image_id=data["Images"]["imageId"],
        tile_size=Size(int(data["Images"]["Tiles"]["width"]),
                       int(data["Images"]["Tiles"]["height"])),
        image_sizes=_parse_image_sizes(data["Images"]["Zooms"]),

        neighbors=_parse_neighbors(annotation["Graph"]["Nodes"],
                                   annotation["Connections"],
                                   panoid),
        links=_parse_links(annotation["Thoroughfares"]),
        historical=_parse_historical(annotation["HistoricalPanoramas"], panoid),

        date=_get_date_from_panoid(panoid),
        height=int(data["Point"]["coordinates"][2]),
        street_name=data["Point"]["name"],

        places=_parse_companies(annotation["Companies"]),
        addresses=addresses,
        other_markers=other_markers,

        author=try_get(lambda: pano_dict["Author"]["name"]),
        author_avatar_url=try_get(lambda: pano_dict["Author"]["avatarUrlTemplate"]),
    )


def _parse_companies(companies_json: list) -> List[Place]:
    companies = []
    for company in companies_json:
        companies.append(Place(
            id=int(company["properties"]["id"]),
            lat=company["geometry"]["coordinates"][1],
            lon=company["geometry"]["coordinates"][0],
            name=company["properties"]["name"],
            tags=company["properties"]["tags"],
        ))
    return companies


def _parse_markers(markers_json: list) -> Tuple[List[Address], List[Marker]]:
    addresses = []
    other_markers = []
    for marker in markers_json:
        # Address markers are displayed at a height of 7 m;
        # all others, like metro icons, have a height of 2 m.
        if marker["geometry"]["coordinates"][2] == 7:
            addresses.append(Address(
                lat=marker["geometry"]["coordinates"][1],
                lon=marker["geometry"]["coordinates"][0],
                house_number=marker["properties"]["name"],
                street_name_and_house_number=marker["properties"]["description"],
            ))
        else:
            other_markers.append(Marker(
                lat=marker["geometry"]["coordinates"][1],
                lon=marker["geometry"]["coordinates"][0],
                name=marker["properties"]["name"],
                description=marker["properties"]["description"],
                style=marker["properties"]["style"],
            ))

    return addresses, other_markers


def _parse_links(links_json):
    links = []
    for link_json in links_json:
        panoid = _get_panoid_from_url(link_json["Connection"]["href"])
        angle = math.radians(float(link_json["Direction"][0]))
        links.append(Link(panoid, angle))
    return links


def _get_panoid_from_url(url: str) -> str:
    return re.findall(r"oid=(.*?)&", url)[0]


def _get_date_from_panoid(panoid: str) -> datetime:
    return datetime.fromtimestamp(int(panoid.split("_")[-1]), timezone.utc)


def _parse_image_sizes(zooms: dict) -> List[Size]:
    sizes = [None] * len(zooms)
    for zoom in zooms:
        idx = int(zoom["level"])
        sizes[idx] = Size(int(zoom["width"]), int(zoom["height"]))
    return sizes


def _parse_neighbors(nodes: List[dict], connections: List[dict], parent_id: str) -> List[YandexPanorama]:
    panos = []
    for node in nodes:
        panoid = node["panoid"]
        if panoid == parent_id:
            continue
        pano = YandexPanorama(
            id=panoid,
            lat=float(node["lat"]),
            lon=float(node["lon"]),
            date=_get_date_from_panoid(panoid),
        )
        panos.append(pano)

    for connection in connections:
        panoid = _get_panoid_from_url(connection["href"])
        pano = YandexPanorama(
            id=panoid,
            lat=connection["Point"]["coordinates"][1],
            lon=connection["Point"]["coordinates"][0],
            height=connection["Point"]["coordinates"][2],
            date=_get_date_from_panoid(panoid),
        )
        panos.append(pano)

    return panos


def _parse_historical(historical: List[dict], parent_id: str) -> List[YandexPanorama]:
    panos = []
    for raw_pano in historical:
        panoid = raw_pano["Connection"]["oid"]
        if panoid == parent_id:
            continue
        pano = YandexPanorama(
            id=panoid,
            lat=float(raw_pano["Connection"]["Point"]["coordinates"][1]),
            lon=float(raw_pano["Connection"]["Point"]["coordinates"][0]),
            height=int(raw_pano["Connection"]["Point"]["coordinates"][2]),
            date=_get_date_from_panoid(panoid)
        )
        panos.append(pano)
    panos = sorted(panos, key=lambda x: x.date, reverse=True)
    return panos
