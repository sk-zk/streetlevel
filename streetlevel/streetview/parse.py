import math
from typing import List, Tuple, Optional
from datetime import datetime

from streetlevel.dataclasses import Link, Size
from streetlevel.geo import get_bearing
from streetlevel.streetview.panorama import StreetViewPanorama, LocalizedString, UploadDate, \
    CaptureDate, Place, BusinessStatus, ArtworkLink, Artwork, BuildingLevel, StreetLabel
from streetlevel.streetview.depth import parse as parse_depth
from streetlevel.streetview.util import is_third_party_panoid
from streetlevel.util import try_get


def parse_panorama_id_response(response: dict) -> Optional[StreetViewPanorama]:
    response_code = response[1][0][0][0]
    # 1: OK
    # 2: Not found
    # don't know if there are others
    if response_code != 1:
        return None
    return parse_panorama_message(response[1][0])


def parse_panorama_radius_response(response: dict) -> Optional[StreetViewPanorama]:
    response_code = response[0][0][0]
    # 0: OK
    # 5: search returned no images
    # don't know if there are others
    if response_code != 0:
        return None
    return parse_panorama_message(response[0][1])


def parse_coverage_tile_response(tile: list) -> List[StreetViewPanorama]:
    if tile is None:
        return []

    panos = []
    if tile[1] is not None and len(tile[1]) > 0:
        for raw_pano in tile[1][1]:
            if raw_pano[0][0] == 1:
                continue
            panos.append(
                StreetViewPanorama(id=raw_pano[0][0][1],
                                   lat=raw_pano[0][2][0][2],
                                   lon=raw_pano[0][2][0][3],
                                   heading=math.radians(raw_pano[0][2][2][0]),
                                   pitch=math.radians(90 - raw_pano[0][2][2][1]),
                                   roll=math.radians(raw_pano[0][2][2][2]),
                                   elevation=raw_pano[0][2][1][0]))
        for idx, raw_pano in enumerate(tile[1][1]):
            link_indices = raw_pano[1]
            panos[idx].links = [Link(panos[link_idx],
                                     get_bearing(panos[idx].lat, panos[idx].lon,
                                                 panos[link_idx].lat, panos[link_idx].lon))
                                for link_idx in link_indices]
    return panos


def parse_panorama_message(msg: dict) -> StreetViewPanorama:
    panoid = msg[1][1]

    img_sizes = msg[2][3][0]
    img_sizes = list(map(lambda x: Size(x[0][1], x[0][0]), img_sizes))
    others = try_get(lambda: msg[5][0][3][0])

    if is_third_party_panoid(panoid) and msg[12] and msg[12][0] != "":
        timestamp = int(msg[12][0].split("/")[1]) / 1000
        date = datetime.fromtimestamp(timestamp)
    else:
        date = try_get(lambda: msg[6][7])
        date = CaptureDate(date[0],
                           date[1],
                           date[2] if len(date) > 2 else None) if date else None

    links, other_bld_levels, other_dates = _parse_other_pano_indices(msg)

    street_names = try_get(lambda: msg[5][0][12])
    if street_names is not None:
        street_names = [_parse_street_name(street_name) for street_name in street_names]

    address = try_get(lambda: msg[3][2])
    if address is not None:
        address = [LocalizedString(x[0], x[1]) for x in address]

    depth = try_get(lambda: msg[5][0][5][1][2])
    if depth:
        depth = parse_depth(depth)

    upload_date = try_get(lambda: msg[6][8])
    if upload_date:
        upload_date = UploadDate(*upload_date)

    places_raw = try_get(lambda: msg[5][0][9])
    if places_raw:
        artworks, places = _parse_places(places_raw)
    else:
        artworks, places = None, None

    pano = StreetViewPanorama(
        id=panoid,
        lat=msg[5][0][1][0][2],
        lon=msg[5][0][1][0][3],
        heading=try_get(lambda: math.radians(msg[5][0][1][2][0])),
        pitch=try_get(lambda: math.radians(90 - msg[5][0][1][2][1])),
        roll=try_get(lambda: math.radians(msg[5][0][1][2][2])),
        depth=depth,
        date=date,
        upload_date=upload_date,
        elevation=try_get(lambda: msg[5][0][1][1][0]),
        tile_size=Size(msg[2][3][1][0], msg[2][3][1][1]),
        image_sizes=img_sizes,
        source=try_get(lambda: msg[6][5][2].lower()),
        country_code=try_get(lambda: msg[5][0][1][4]),
        street_names=street_names,
        address=address,
        copyright_message=try_get(lambda: msg[4][0][0][0][0]),
        uploader=try_get(lambda: msg[4][1][0][0][0]),
        uploader_icon_url=try_get(lambda: msg[4][1][0][2]),
        building_level=_parse_building_level_message(try_get(lambda: msg[5][0][1][3])),
        artworks=artworks,
        places=places,
    )

    # parse other dates, links and neighbors
    if others is not None:
        for idx, other in enumerate(others):
            other_id = other[0][1]
            if pano.id == other_id:
                continue

            connected = StreetViewPanorama(
                id=other_id,
                lat=try_get(lambda: float(other[2][0][2])),
                lon=try_get(lambda: float(other[2][0][3])),
                elevation=try_get(lambda: other[2][1][0]),
                heading=try_get(lambda: math.radians(other[2][2][0])),
                pitch=try_get(lambda: math.radians(90 - other[2][2][1])),
                roll=try_get(lambda: math.radians(other[2][2][2])),
                building_level=_parse_building_level_message(try_get(lambda: other[2][3])),
            )

            if idx in other_dates:
                if other_dates[idx]:
                    connected.date = CaptureDate(other_dates[idx][0], other_dates[idx][1])
                pano.historical.append(connected)
            else:
                if idx in links:
                    if links[idx]:
                        angle = math.radians(links[idx][3])
                    else:
                        angle = get_bearing(pano.lat, pano.lon, connected.lat, connected.lon)
                    pano.links.append(Link(connected, angle))
                if idx in other_bld_levels:
                    pano.building_levels.append(connected)
                pano.neighbors.append(connected)

            other_address = try_get(lambda: other[3][2])
            if other_address:
                connected.address = [LocalizedString(x[0], x[1]) for x in other_address]

    pano.historical = sorted(pano.historical,
                             key=lambda x: (x.date.year, x.date.month) if x.date else None,
                             reverse=True)

    return pano


def _parse_street_name(msg: dict) -> StreetLabel:
    # Unknown what [0][0][0][1] is, but it may be something interesting, always 2 numbers as a string
    name_raw = msg[0][0][2]
    name = LocalizedString(name_raw[0], name_raw[1])
    angles = [math.radians(angle) for angle in msg[1]]
    return StreetLabel(name, angles)


def _parse_other_pano_indices(msg: dict) -> Tuple[dict, list, dict]:
    links_raw = try_get(lambda: msg[5][0][6])
    if links_raw:
        links = dict([(x[0], try_get(lambda: x[1])) for x in links_raw])
    else:
        links = {}

    other_bld_levels_raw = try_get(lambda: msg[5][0][7])
    if other_bld_levels_raw:
        other_bld_levels = [x[0] for x in other_bld_levels_raw]
    else:
        other_bld_levels = []

    other_dates_raw = try_get(lambda: msg[5][0][8])
    if other_dates_raw:
        other_dates = dict([(x[0], x[1]) for x in other_dates_raw])
    else:
        other_dates = {}
    return links, other_bld_levels, other_dates


def _parse_building_level_message(bld_level: Optional[list]) -> Optional[BuildingLevel]:
    if bld_level and len(bld_level) > 1:
        return BuildingLevel(
            bld_level[1],
            try_get(lambda: LocalizedString(*bld_level[2])),
            try_get(lambda: LocalizedString(*bld_level[3])))
    return None


def _parse_places(places_raw: list) -> Tuple[List[Artwork], List[Place]]:
    artworks = []
    places = []
    for place in places_raw:
        # There are multiple types of objects that can be returned here, only way to differentiate them is the length
        if len(place) == 6:
            artwork = _parse_artwork(place)
            artworks.append(artwork)
        elif len(place) == 8:
            places.append(_parse_place(place))
    return artworks, places


def _parse_artwork(place: dict) -> Artwork:
    marker_yaw = try_get(lambda: place[1][0][0][0])
    if marker_yaw:
        marker_yaw = _marker_yaw_to_rad(marker_yaw)
    marker_pitch = try_get(lambda: place[1][0][0][1])
    if marker_pitch:
        marker_pitch = _marker_pitch_to_rad(marker_pitch)

    if len(place[5]) > 9:
        link = ArtworkLink(place[5][9][0][1], LocalizedString(*place[5][9][1]))
    else:
        link = None

    artwork = Artwork(
        id=try_get(lambda: place[0][2][0]),
        title=LocalizedString(*place[5][0]),
        description=try_get(lambda: LocalizedString(*place[5][1])),
        thumbnail=place[5][3],
        creator=try_get(lambda: LocalizedString(*place[5][6])),
        url=try_get(lambda: place[5][7][1][0]),
        attributes={prop[0][0]: LocalizedString(*prop[1]) for prop in place[5][2]} if place[5][2] else {},
        marker_icon_url=place[4],
        marker_yaw=marker_yaw,
        marker_pitch=marker_pitch,
        link=link
    )
    return artwork


def _parse_place(place: dict) -> Place:
    feature_id_parts = place[0][1]
    feature_id = ':'.join(hex(int(part)) for part in feature_id_parts)
    cid = try_get(lambda: int(place[0][3]))
    if cid is None:
        cid = int(place[0][1][1])

    marker_yaw = try_get(lambda: place[1][0][0][0])
    if marker_yaw:
        marker_yaw = _marker_yaw_to_rad(marker_yaw)
    marker_pitch = try_get(lambda: place[1][0][0][1])
    if marker_pitch:
        marker_pitch = _marker_pitch_to_rad(marker_pitch)
    marker_distance = try_get(lambda: place[1][0][0][2])

    return Place(feature_id=feature_id,
                 cid=cid,
                 marker_yaw=marker_yaw,
                 marker_pitch=marker_pitch,
                 marker_distance=marker_distance,
                 name=try_get(lambda: LocalizedString(*place[2])),
                 type=try_get(lambda: LocalizedString(*place[3])),
                 marker_icon_url=place[4],
                 status=BusinessStatus(place[7]))


def _marker_yaw_to_rad(marker_yaw: float) -> float:
    return (marker_yaw - 0.5) * math.tau


def _marker_pitch_to_rad(marker_pitch: float) -> float:
    return (0.5 - marker_pitch) * math.pi
