from io import BytesIO
import itertools
import json
import os
from PIL import Image
import requests
import time
from .maps import *
from .panorama import StreetViewPanorama
from .protobuf import *


def is_third_party_panoid(panoid):
    """
    Returns whether a panoid refers to a third-party panorama.
    """
    return len(panoid) > 22


def _split_ietf(tag):
    """
    Splits an IETF language tag into its language part and country part.
    """
    tag = tag.split("-")
    lang = tag[0]
    country = tag[1] if len(tag) > 1 else tag[0]
    return lang, country


def _try_get(accessor):
    try:
        return accessor()
    except IndexError:
        return None


def _find_panorama_raw(lat, lon, radius=50, download_depth=False, locale="en", session=None):
    radius = float(radius)
    toggles = []
    search_third_party = False
    include_resolution_info = True
    include_street_name_and_date = True
    include_copyright_information = True
    include_neighbors_and_historical = True
    ietf_lang, ietf_country = _split_ietf(locale)

    if search_third_party:
        image_type = 10
    else:
        image_type = 2

    if download_depth:
        depth1 = {1: ProtobufEnum(0)}
        depth2 = {1: ProtobufEnum(2)}
    else:
        depth1 = {}
        depth2 = {}

    if include_resolution_info:
        toggles.append(ProtobufEnum(1))
    if include_street_name_and_date:
        toggles.append(ProtobufEnum(2))
    if include_copyright_information:
        toggles.append(ProtobufEnum(3))
    toggles.append(ProtobufEnum(4))
    if include_neighbors_and_historical:
        toggles.append(ProtobufEnum(6))
    toggles.append(ProtobufEnum(8))

    search_message = {
        1: {
            1: 'apiv3',
            5: 'US',
            11: {1: {1: False}}
        },
        2: {1: {3: lat, 4: lon}, 2: radius},
        3: {
            2: {1: ietf_lang, 2: ietf_country},
            9: {1: ProtobufEnum(2)},
            11: {
                1: {1: ProtobufEnum(image_type), 2: True, 3: ProtobufEnum(2)}
            },
        },
        4: {
            1: toggles,
            5: depth1,
            6: depth2,
        }
    }

    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=" \
          + to_protobuf_url(search_message) + "&callback=_xdc_._v2mub5"

    if session is None:
        response = requests.get(url).text
    else:
        response = session.get(url).text
    first_paren = response.index("(")
    last_paren = response.rindex(")")
    pano_data_json = "[" + response[first_paren + 1:last_paren] + "]"
    pano_data = json.loads(pano_data_json)
    return pano_data


def find_panorama(lat, lon, radius=50, download_depth=False, locale="en", session=None):
    """
    Searches for a panorama within a radius around a point.
    """
    resp = _find_panorama_raw(lat, lon, radius=radius, download_depth=download_depth,
                              locale=locale, session=session)

    response_code = resp[0][0][0]
    # 0: OK
    # 5: search returned no images
    # don't know if there are others
    if response_code != 0:
        return None

    pano = _parse_pano_message(resp[0][1])
    return pano


def _lookup_panoid_raw(panoid, download_depth=False, locale="en", session=None):
    pano_type = 10 if is_third_party_panoid(panoid) else 2
    toggles = []
    include_resolution_info = True
    include_street_name_and_date = True
    include_copyright_information = True
    include_neighbors_and_historical = True
    ietf_lang, ietf_country = _split_ietf(locale)

    if include_resolution_info:
        toggles.append(ProtobufEnum(1))
    if include_street_name_and_date:
        toggles.append(ProtobufEnum(2))
    if include_copyright_information:
        toggles.append(ProtobufEnum(3))
    toggles.append(ProtobufEnum(4))  # does nothing?
    toggles.append(ProtobufEnum(5))  # does nothing?
    if include_neighbors_and_historical:
        toggles.append(ProtobufEnum(6))

    # these change stuff, but idk what exactly:
    toggles.append(ProtobufEnum(8))
    # toggles.append(ProtobufEnum(11))
    toggles.append(ProtobufEnum(12))
    # toggles.append(ProtobufEnum(13))

    if download_depth:
        depth1 = [{1: ProtobufEnum(1)}, {1: ProtobufEnum(2)}]
        depth2 = [{1: ProtobufEnum(1)}, {1: ProtobufEnum(2)}]
    else:
        depth1 = [{}]
        depth2 = [{}]

    # this is the protobuf message in the request URL written out as a dict
    pano_request_message = {
        1: {1: 'maps_sv.tactile', 11: {2: {1: True}}},
        2: {1: ietf_lang, 2: ietf_country},
        3: {1: {1: ProtobufEnum(pano_type), 2: panoid}},
        4: {
            1: toggles,
            2: {1: ProtobufEnum(1)},  # changing this to any other value causes huge changes;
            # haven't looked into it any further though
            4: {1: 48},  # all this does is change the size param in an icon URL
            5: depth1,
            6: depth2,
            9: {  # none of these seem to do anything
                1: [
                    {1: ProtobufEnum(2), 2: True, 3: ProtobufEnum(2)},
                    {1: ProtobufEnum(2), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(3), 2: True, 3: ProtobufEnum(2)},
                    {1: ProtobufEnum(3), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(8), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(1), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(4), 2: False, 3: ProtobufEnum(3)},
                    {1: ProtobufEnum(10), 2: True, 3: ProtobufEnum(2)},
                    {1: ProtobufEnum(10), 2: False, 3: ProtobufEnum(3)}
                ]
            }
        }
    }
    url = f"https://www.google.com/maps/photometa/v1?authuser=0&hl={ietf_lang}&gl={ietf_country}&pb=" \
          + to_protobuf_url(pano_request_message)

    if session is None:
        response = requests.get(url).text
    else:
        response = session.get(url).text
    pano_data_json = response[4:]  # skip that junk at the start
    pano_data = json.loads(pano_data_json)
    return pano_data


def lookup_panoid(panoid, download_depth=False, locale="en", session=None):
    """
    Fetches metadata for a specific panorama.
    """
    resp = _lookup_panoid_raw(panoid, download_depth=download_depth,
                              locale=locale, session=session)

    response_code = resp[1][0][0][0]
    # 1: OK
    # 2: Not found
    # don't know if there are others
    if response_code != 1:
        return None

    pano = _parse_pano_message(resp[1][0])
    return pano


def _parse_pano_message(msg):
    img_sizes = msg[2][3][0]
    img_sizes = list(map(lambda x: x[0], img_sizes))
    panoid = msg[1][1]
    lat = msg[5][0][1][0][2]
    lon = msg[5][0][1][0][3]
    others = _try_get(lambda: msg[5][0][3][0])
    date = msg[6][7]
    try:
        other_dates = msg[5][0][8]
        other_dates = dict([(x[0], x[1]) for x in other_dates])
    except (IndexError, TypeError):
        other_dates = {}

    pano = StreetViewPanorama(
        id=panoid,
        lat=lat,
        lon=lon,
        year=date[0],
        month=date[1],
        day=date[2] if len(date) > 2 else None,
        tile_size=msg[2][3][1],
        image_sizes=img_sizes,
        country_code=_try_get(lambda: msg[5][0][1][4]),
        street_name=_try_get(lambda: msg[5][0][12][0][0][0][2]),
        address=_try_get(lambda: msg[3][2]),
        copyright_message=_try_get(lambda: msg[4][0][0][0][0]),
        uploader=_try_get(lambda: msg[4][1][0][0][0]),
        uploader_icon_url=_try_get(lambda: msg[4][1][0][2]),
    )

    # parse neighbors and other dates
    if others is not None and len(others) > 1:
        for idx, other in enumerate(others[1:], start=1):
            panoid = other[0][1]
            lat = float(other[2][0][2])
            lon = float(other[2][0][3])

            neighbor_or_historical = StreetViewPanorama(panoid, lat, lon)

            if idx in other_dates:
                neighbor_or_historical.year = other_dates[idx][0]
                neighbor_or_historical.month = other_dates[idx][1]
                pano.historical.append(neighbor_or_historical)
            else:
                pano.neighbors.append(neighbor_or_historical)

            neighbor_or_historical.street_name = _try_get(lambda: other[3][2][0])
    pano.historical = sorted(pano.historical, key=lambda x: (x.year, x.month), reverse=True)

    return pano


def download_panorama(pano, filename, zoom=5):
    """
    Downloads a panorama.
    """
    stitched = get_panorama(pano, zoom=zoom)
    stitched.save(filename)


def get_panorama(pano, zoom=5):
    """
    Downloads a panorama as PIL image.
    """
    zoom = min(zoom, len(pano.image_sizes) - 1)
    tile_list = _generate_tile_list(pano, zoom)
    tiles = _download_tiles(tile_list)
    stitched = _stitch_tiles(pano, tile_list, tiles, zoom)
    return stitched


def _generate_tile_list(pano, zoom):
    """
    Generates a list of a panorama's tiles.
    Returns a list of (x, y, tile_url) tuples.
    """
    img_size = pano.image_sizes[zoom]
    tile_width = pano.tile_size[0]
    tile_height = pano.tile_size[1]
    cols = math.ceil(img_size[1] / tile_width)
    rows = math.ceil(img_size[0] / tile_height)

    image_url = "https://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom={3:}&x={1:}&y={2:}"
    third_party_image_url = "https://lh3.ggpht.com/p/{0:}=x{1:}-y{2:}-z{3:}"

    url_to_use = third_party_image_url if is_third_party_panoid(pano.id) else image_url

    coord = list(itertools.product(range(cols), range(rows)))
    tiles = [(x, y, url_to_use.format(pano.id, x, y, zoom)) for x, y in coord]
    return tiles


def _download_tiles(tile_list, session=None):
    """
    Downloads tiles from a tile list generated by _generate_tile_list().
    """
    if session is None:
        session = requests.Session()

    tile_data = {}
    for i, (x, y, url) in enumerate(tile_list):
        response = session.get(url, stream=True)
        tile_data[(x, y)] = response.content
        del response

    return tile_data


def _stitch_tiles(pano, tile_list, tile_data, zoom):
    """
    Stitches downloaded tiles to a full image.
    """
    img_size = pano.image_sizes[zoom]
    tile_width = pano.tile_size[0]
    tile_height = pano.tile_size[1]
    cols = math.ceil(img_size[1] / tile_width)
    rows = math.ceil(img_size[0] / tile_height)

    panorama = Image.new('RGB', (img_size[1], img_size[0]))

    for x, y, url in tile_list:
        tile = Image.open(BytesIO(tile_data[(x, y)]))
        panorama.paste(im=tile, box=(x * tile_width, y * tile_height))
        del tile

    return panorama


def get_coverage_tile(tile_x, tile_y, session=None):
    """
    Gets all panoramas on a Google Maps tile (at zoom level 17 specifically, for some reason).
    Returns panoid, lat, lon only.
    This function uses the API call which is triggered when zooming into a tile in globe view on Google Maps,
    so it can be used to find hidden coverage.
    Unlike get_panos_at_position(), the list only contains the most recent panorama of a location.
    """
    resp = _get_coverage_tile_raw(tile_x, tile_y, session)

    if resp is None:
        return []

    panos = []
    if resp[1] is not None and len(resp[1]) > 0:
        for pano in resp[1][1]:
            if pano[0][0] == 1:
                continue
            panoid = pano[0][0][1]
            lat = pano[0][2][0][2]
            lon = pano[0][2][0][3]
            panos.append(StreetViewPanorama(panoid, lat, lon))

    return panos


def _get_coverage_tile_raw(tile_x, tile_y, session=None):
    url = "https://www.google.com/maps/photometa/ac/v1?pb=!1m1!1smaps_sv.tactile!6m3!1i{0}!2i{1}!3i17!8b1"
    url = url.format(tile_x, tile_y)
    if session is None:
        response = requests.get(url).text
    else:
        response = session.get(url).text
    data_json = response[4:]
    data = json.loads(data_json)
    return data


def get_coverage_tile_by_latlon(lat, lon, session=None):
    """
    Gets all panoramas on a Google Maps tile (at zoom level 17 specifically, for some reason).
    Returns panoid, lat, lon only.
    This function uses the API call which is triggered when zooming into a tile in globe view on Google Maps,
    so it can be used to find hidden coverage.
    Unlike get_panos_at_position(), the list only contains the most recent panorama of a location.
    """
    tile_coord = wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(tile_coord[0], tile_coord[1], session=session)
