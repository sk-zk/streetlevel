import math
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Union

from .panorama import BaiduPanorama, PanoInteriorMetadata, PanoInteriorPoint, \
    User, Provider, InteriorMetadata, Floor, InteriorPoint
from ..dataclasses import Size
from ..geo import bd09mc_to_wgs84


_tz = timezone(timedelta(hours=8), "Asia/Shanghai")


def parse_panorama_response(response: dict) -> Optional[BaiduPanorama]:
    if response["result"]["error"] != 0:
        return None

    if len(response["content"]) == 0:
        return None

    pano = response["content"][0]
    x, y, lat, lon = _convert_position(pano["X"], pano["Y"])

    return BaiduPanorama(
        id=pano["ID"],
        x=x,
        y=y,
        lat=lat,
        lon=lon,
        elevation=pano["Z"],
        heading=math.radians(pano["Heading"]),
        pitch=math.radians(pano["Pitch"]),
        roll=math.radians(pano["Roll"]),
        date=_parse_date_from_panoid(pano["ID"]),
        image_sizes=[Size(x["BlockX"] * 256, x["BlockY"] * 256) for x in pano["ImgLayer"]],
        neighbors=_parse_neighbors(pano["Roads"]),
        historical=_parse_historical(pano["TimeLine"]),
        street_name=pano["Rname"],
        provider=_parse_provider(pano["Provider"]),
        height=pano["DeviceHeight"],
        creator=_parse_user(pano),
        interior=_parse_pano_inter(pano),
    )


def _parse_provider(raw_provider: int) -> Union[int, Provider]:
    if raw_provider in [8, 9, 10, 14]:
        provider = Provider.BAIDU
    else:
        try:
            provider = Provider(raw_provider)
        except ValueError:
            provider = raw_provider
    return provider


def _parse_provider_from_panoid(panoid: str) -> Union[int, Provider]:
    return _parse_provider(int(panoid[0:2]))


def _convert_position(x: float, y: float) -> Tuple[float, float, float, float]:
    x, y = x / 100.0, y / 100.0
    lat, lon = bd09mc_to_wgs84(x, y)
    return x, y, lat, lon


def _parse_user(pano: dict) -> Optional[User]:
    if "Username" not in pano:
        return None
    if pano["Username"] == "" and pano["UserID"] == "":
        return None
    return User(
        name=pano["Username"],
        id=pano["UserID"]
    )


def _parse_pano_inter(pano: dict) -> Optional[PanoInteriorMetadata]:
    if "Inters" not in pano or len(pano["Inters"]) == 0:
        return None

    inter_panos = []
    for photo in pano["Photos"]:
        inter_panos.append(PanoInteriorPoint(
            id=photo["PID"],
            name=photo["Name"],
            floor=photo["Floor"],
            date=_parse_date_from_panoid(photo["PID"])
        ))

    inter = pano["Inters"][0]  # don't know if there can be more than one of these

    meta = PanoInteriorMetadata(
        id=inter["IID"],
        exit_panoid=inter["BreakID"],
        uid=inter["UID"],
        name=inter["Name"],
        panos=inter_panos
    )
    if "X" in inter:
        meta.x, meta.y = inter["X"], inter["Y"]
        meta.lat, meta.lon = bd09mc_to_wgs84(meta.x, meta.y)
    return meta


def _parse_neighbors(roads: List[dict]) -> List[BaiduPanorama]:
    if not roads or len(roads) == 0:
        return []

    neighbors = []
    for road in roads:
        if "Panos" not in road or not road["Panos"]:
            continue
        for pano in road["Panos"]:
            x, y = pano["X"] / 100.0, pano["Y"] / 100.0
            lat, lon = bd09mc_to_wgs84(x, y)
            neighbors.append(BaiduPanorama(
                id=pano["PID"],
                x=x,
                y=y,
                lat=lat,
                lon=lon,
                date=_parse_date_from_panoid(pano["PID"]),
                provider=_parse_provider_from_panoid(pano["PID"])
            ))
    return neighbors


def _parse_historical(timeline: dict) -> List[BaiduPanorama]:
    if not timeline:
        return []

    historical = []
    for entry in timeline:
        if entry["IsCurrent"] == 1:
            continue
        historical.append(BaiduPanorama(
            id=entry["ID"],
            date=_parse_date_from_panoid(entry["ID"]),
            x=0,
            y=0,
            lat=0,
            lon=0,
            provider=_parse_provider_from_panoid(entry["ID"])
        ))
    return historical


def _parse_date_from_panoid(panoid: str) -> datetime:
    year, month, day = 2000 + int(panoid[10:12]), int(panoid[12:14]), int(panoid[14:16])
    hour, minute, second = int(panoid[16:18]), int(panoid[18:20]), int(panoid[20:22])
    return datetime(year=year, month=month, day=day,
                    hour=hour, minute=minute, second=second,
                    tzinfo=_tz)


def parse_inter_response(response: dict) -> Optional[InteriorMetadata]:
    if response["result"]["error"] != 0:
        return None

    if len(response["content"]) == 0:
        return None

    inter = response["content"][0]["interinfo"]
    if "BreakID" in inter and inter["BreakID"] != "":
        bx, by, blat, blon = _convert_position(inter["BreakX"], inter["BreakY"])
        exit_pano = BaiduPanorama(
            id=inter["BreakID"],
            x=bx,
            y=by,
            lat=blat,
            lon=blon,
            date=_parse_date_from_panoid(inter["BreakID"]),
            provider=_parse_provider_from_panoid(inter["BreakID"])
        )
    else:
        exit_pano = None
    x, y, lat, lon = _convert_position(inter["IPoint"]["X"], inter["IPoint"]["Y"])
    return InteriorMetadata(
        id=inter["IID"],
        name=inter["Name"],
        uid=inter["UID"],
        x=x,
        y=y,
        lat=lat,
        lon=lon,
        floors=_parse_inter_floors(inter),
        default_floor=inter["Defaultfloor"],
        exit_pano=exit_pano
    )


def _parse_inter_floors(inter: dict) -> List[Floor]:
    floors = []
    for floor in inter["Floors"]:
        points = []
        if "Points" in floor and floor["Points"]:
            for point in floor["Points"]:
                x, y, lat, lon = _convert_position(point["X"], point["Y"])
                points.append(InteriorPoint(
                    name=point["name"],
                    creator=point["ugc"] if point["ugc"] != "" else None,
                    catalog_label=_catalog_id_to_label(point["catalog"]),
                    floor=floor["Floor"],
                    pano=BaiduPanorama(
                        id=point["PID"],
                        x=x,
                        y=y,
                        lat=lat,
                        lon=lon,
                        # TODO is this correct?
                        heading=math.radians(point["movedir"]),
                        date=_parse_date_from_panoid(point["PID"]),
                        provider=_parse_provider_from_panoid(point["PID"])
                )))
        floors.append(Floor(
            number=floor["Floor"],
            name=floor["Name"],
            start_panoid=floor["StartID"],
            panos=points
        ))
    return floors


def _catalog_id_to_label(catalog_id_str: str) -> str:
    labels = ["其他", "正门", "房型", "设施", "正门", "餐饮设施", "其他设施", "正门", "设施", "观影厅", "其他设施"]
    mapping = [0, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 5, 5, 5, 6, 6, 7, 8, 8, 8, 9]
    catalog_id = int(catalog_id_str)
    if catalog_id > len(mapping):
        return catalog_id_str
    return labels[mapping[catalog_id]]
