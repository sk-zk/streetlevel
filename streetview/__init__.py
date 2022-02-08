from io import BytesIO
import itertools
import json
import os
from PIL import Image
import requests
import time
from streetview.panorama import StreetViewPanorama
from streetview.maps import *


def is_third_party_panoid(panoid):
    """
    Returns whether or not a panoid refers to a third-party panorama.
    """
    return len(panoid) == 44


def get_panos_at_position(lat, lon, radius=50, session=None):
    """
    Searches for panoramas around a point.
    """
    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d{2}!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e0!6m1!1e2&callback=_xdc_._v2mub5"
    url = url.format(lat, lon, radius)

    if session == None:
        resp = requests.get(url).text
    else:
        resp = session.get(url).text

    # remove all that junk surrounding the json data
    first_paren = resp.index("(")
    last_paren = resp.rindex(")")
    pano_data_json = "[" + resp[first_paren + 1:last_paren] + "]"
    pano_data = json.loads(pano_data_json)

    try:
        img_sizes = pano_data[0][1][2][3][0]
    except IndexError:  # search returned no images
        return []
    img_sizes = list(map(lambda x: x[0], img_sizes))
    tile_size = pano_data[0][1][2][3][1]
    response_panos = pano_data[0][1][5][0][3][0]
    most_recent_date = pano_data[0][1][6][7]
    try:
        other_dates = pano_data[0][1][5][0][8]
        other_dates = dict([(x[0], x[1]) for x in other_dates])
    except (IndexError, TypeError):
        other_dates = {}

    panos = []

    for idx, pano in enumerate(response_panos):
        panoid = pano[0][1]
        lat = float(pano[2][0][2])
        lon = float(pano[2][0][3])

        pano_obj = StreetViewPanorama(panoid, lat, lon)

        if idx == 0:
            pano_obj.year = most_recent_date[0]
            pano_obj.month = most_recent_date[1]
            panos.append(pano_obj)
        elif idx in other_dates:
            pano_obj.year = other_dates[idx][0]
            pano_obj.month = other_dates[idx][1]
            panos[0].historical.append(pano_obj)
        else:
            panos.append(pano_obj)

        try:
            pano_obj.street_name = pano[3][2][0]
        except IndexError:
            pass

        pano_obj.tile_size = tile_size
        pano_obj.image_sizes = img_sizes

    panos[0].historical = sorted(panos[0].historical, key=lambda x: (x.year, x.month), reverse=True)
    return panos


def lookup_panoid(panoid, session=None, download_depth=False):
    """
    Fetches metadata for a specific panorama.
    """
    pano_type = 10 if is_third_party_panoid(panoid) else 2
    depth_toggle = 2 if download_depth else 0
    url = "https://www.google.com/maps/photometa/v1?authuser=0&hl=de&gl=de&pb=!1m4!1smaps_sv.tactile!11m2!2m1!1b1!2m2!1sde!2sde!3m3!1m2!1e{0}!2s{1}!4m57!1e1!1e2!1e3!1e4!1e5!1e6!1e8!1e12!2m1!1e1!4m1!1i48!5m1!1e1!5m1!1e{2}!6m1!1e1!6m1!1e2!9m36!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e1!2b0!3e3!1m3!1e4!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e3"
    url = url.format(pano_type, panoid, depth_toggle)
    if session == None:
        response = requests.get(url).text
    else:
        response = session.get(url).text
    pano_data_json = response[4:]  # skip that junk at the start
    pano_data = json.loads(pano_data_json)

    try:
        img_sizes = pano_data[1][0][2][3][0]
    except TypeError:  # lookup returned nothing
        return None
    img_sizes = list(map(lambda x: x[0], img_sizes))
    tile_size = pano_data[1][0][2][3][1]
    lat = pano_data[1][0][5][0][1][0][2]
    lon = pano_data[1][0][5][0][1][0][3]
    date = pano_data[1][0][6][7]

    try:
        country_code = pano_data[1][0][5][0][1][4]
    except IndexError:
        country_code = None
    try:
        street_name = pano_data[1][0][5][0][12][0][0][0][2]
    except IndexError:
        street_name = None

    neighbors = pano_data[1][0][5][0][3][0]

    # TODO: Properly parse historical panos & neighbors

    pano = StreetViewPanorama(panoid, lat, lon)
    pano.month = date[1]
    pano.year = date[0]
    pano.neighbors = neighbors
    #pano.historical =
    pano.tile_size = tile_size
    pano.image_sizes = img_sizes
    pano.country_code = country_code
    pano.street_name = street_name
    return pano


def download_panorama(pano, directory, zoom=5):
    """
    Downloads a panorama to the given directory.
    """
    stitched = get_panorama(pano, zoom=zoom)
    stitched.save(os.path.join(directory, f"{pano.id}.jpg"))
    del stitched


def get_panorama(pano, zoom=5):
    """
    Downloads a panorama as PIL image.
    """
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

    image_url = "http://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom={3:}&x={1:}&y={2:}"
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
        while True:
            try:
                response = session.get(url, stream=True)
                break
            except requests.ConnectionError:
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)

        tile_data[(x,y)] = response.content
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
        tile = Image.open(BytesIO(tile_data[(x,y)]))
        panorama.paste(im=tile, box=(x*tile_width, y*tile_height))
        del tile

    return panorama


def get_coverage_tile(tile_x, tile_y, session=None):
    """
    Gets all panoramas on a Google Maps tile (at zoom level 17 specifially, for some reason).
    Returns panoid, lat, lon only.
    This function uses the API call which is triggered when zooming into a tile in globe view on Google Maps,
    so it can be used to find hidden coverage.
    Unlike get_panos_at_position(), the list only contains the most recent panorama of a location.
    """
    url = "https://www.google.com/maps/photometa/ac/v1?pb=!1m1!1smaps_sv.tactile!6m3!1i{0}!2i{1}!3i17!8b1"
    url = url.format(tile_x, tile_y)
    if session is None:
        response = requests.get(url).text
    else:
        response = session.get(url).text
    data_json = response[4:]
    data = json.loads(data_json)

    if data is None:
        return []

    panos = []
    if data[1] is not None and len(data[1]) > 0:
        for pano in data[1][1]:
            if pano[0][0] == 1:
                continue
            panoid = pano[0][0][1]
            lat = pano[0][2][0][2]
            lon = pano[0][2][0][3]
            panos.append(StreetViewPanorama(panoid, lat, lon))

    return panos


def get_coverage_tile_by_latlon(lat, lon, session=None):
    """
    Gets all panoramas on a Google Maps tile (at zoom level 17 specifially, for some reason).
    Returns panoid, lat, lon only.
    This function uses the API call which is triggered when zooming into a tile in globe view on Google Maps,
    so it can be used to find hidden coverage.
    Unlike get_panos_at_position(), the list only contains the most recent panorama of a location.
    """
    tile_coord = wgs84_to_tile_coord(lat, lon, 17)
    return get_coverage_tile(tile_coord[0], tile_coord[1], session=session)
