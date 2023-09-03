from pytest import approx
import json
from streetlevel import streetview
from streetlevel.dataclasses import Size


def mocked_find_panorama_by_id_raw(panoid, download_depth=False, locale="en", session=None):
    with open("streetview/data/lookup_object.json", "r") as f:
        return json.load(f)


def mocked_find_panorama_by_id_raw_async(panoid, session, download_depth=False, locale="en"):
    with open("streetview/data/lookup_object.json", "r") as f:
        return json.load(f)


def mocked_find_panorama_raw(lat, lon, radius=50, download_depth=False, locale="en",
                             search_third_party=False, session=None):
    with open("streetview/data/find_object.json", "r") as f:
        return json.load(f)


async def mocked_find_panorama_raw_async(lat, lon, session, radius=50, download_depth=False, locale="en",
                                         search_third_party=False):
    with open("streetview/data/find_object.json", "r") as f:
        return json.load(f)


def mocked_get_coverage_tile_raw(tile_x, tile_y, session=None):
    with open("streetview/data/coverage_tile_object.json", "r") as f:
        return json.load(f)


streetview.api.find_panorama_by_id_raw = mocked_find_panorama_by_id_raw
streetview.api.find_panorama_raw = mocked_find_panorama_raw
streetview.api.find_panorama_raw_async = mocked_find_panorama_raw_async
streetview.api.get_coverage_tile_raw = mocked_get_coverage_tile_raw


def test_is_third_party_panoid(request):
    assert not streetview.is_third_party_panoid("n-Zd6bDDL_XOc_jkNgFsGg")
    assert streetview.is_third_party_panoid("AF1QipN3bwjvnpTUbfCZ18wsUMrpZ6Ul2mhVfNKl71_X")


def test_find_panorama_by_id():
    panoid = "n-Zd6bDDL_XOc_jkNgFsGg"
    pano = streetview.find_panorama_by_id(panoid, download_depth=False, session=None)
    assert pano.id == panoid
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)
    assert pano.date.month == 3
    assert pano.date.year == 2021
    assert pano.country_code == "AT"
    assert pano.tile_size == Size(512, 512)
    assert len(pano.image_sizes) == 6
    assert pano.image_sizes[-1] == Size(16384, 8192)


def test_find_panorama():
    pano = streetview.find_panorama(47.15048822721601, 11.13385612403307,
                                    radius=100, session=None)
    assert pano.id == "n-Zd6bDDL_XOc_jkNgFsGg"
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)


async def test_find_panorama_async():
    pano = await streetview.find_panorama_async(47.15048822721601, 11.13385612403307, None, radius=100)
    assert pano.id == "n-Zd6bDDL_XOc_jkNgFsGg"
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)


def test_find_get_coverage_tile_by_latlon():
    panos = streetview.get_coverage_tile_by_latlon(47.15048822721601, 11.13385612403307)
    assert any(p.id == "n-Zd6bDDL_XOc_jkNgFsGg" for p in panos)
