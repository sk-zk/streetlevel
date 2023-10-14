from pytest import approx
import json
from streetlevel import streetview
from streetlevel.dataclasses import Size


def test_is_third_party_panoid(request):
    assert not streetview.is_third_party_panoid("n-Zd6bDDL_XOc_jkNgFsGg")
    assert streetview.is_third_party_panoid("AF1QipN3bwjvnpTUbfCZ18wsUMrpZ6Ul2mhVfNKl71_X")


def test_find_panorama_by_id():
    def mocked_find_panorama_by_id_raw(panoid, download_depth=False, locale="en", session=None):
        with open("streetview/data/find_by_id.json", "r") as f:
            return json.load(f)

    streetview.api.find_panorama_by_id_raw = mocked_find_panorama_by_id_raw

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
    def mocked_find_panorama_raw(lat, lon, radius=50, download_depth=False, locale="en",
                                 search_third_party=False, session=None):
        with open("streetview/data/find.json", "r") as f:
            return json.load(f)

    streetview.api.find_panorama_raw = mocked_find_panorama_raw

    pano = streetview.find_panorama(47.15048822721601, 11.13385612403307,
                                    radius=100, session=None)
    assert pano.id == "n-Zd6bDDL_XOc_jkNgFsGg"
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)


async def test_find_panorama_async():
    async def mocked_find_panorama_raw_async(lat, lon, session, radius=50, download_depth=False, locale="en",
                                             search_third_party=False):
        with open("streetview/data/find.json", "r") as f:
            return json.load(f)

    streetview.api.find_panorama_raw_async = mocked_find_panorama_raw_async

    pano = await streetview.find_panorama_async(47.15048822721601, 11.13385612403307, None, radius=100)
    assert pano.id == "n-Zd6bDDL_XOc_jkNgFsGg"
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)


def test_find_get_coverage_tile_by_latlon():
    def mocked_get_coverage_tile_raw(tile_x, tile_y, session=None):
        with open("streetview/data/coverage_tile.json", "r") as f:
            return json.load(f)

    streetview.api.get_coverage_tile_raw = mocked_get_coverage_tile_raw

    panos = streetview.get_coverage_tile_by_latlon(47.15048822721601, 11.13385612403307)
    assert any(p.id == "n-Zd6bDDL_XOc_jkNgFsGg" for p in panos)


def test_nepal_links():
    def mocked_find_panorama_by_id_raw(panoid, download_depth=False, locale="en", session=None):
        with open("streetview/data/nepal_links.json", "r") as f:
            return json.load(f)

    streetview.api.find_panorama_by_id_raw = mocked_find_panorama_by_id_raw

    pano = streetview.find_panorama_by_id("75oFcYmZUOnqgvAaX2q-_w")
    assert pano.links[0].pano.id == "yCIEQ7o37R49IxNPOkhWgw"
    assert pano.links[0].pano.lat is None
    assert pano.links[1].pano.id == "C9aepLhvgmFjRJlP2GxjXQ"
    assert pano.links[1].pano.lat is None


def test_missing_link_direction():
    def mocked_find_panorama_by_id_raw(panoid, download_depth=False, locale="en", session=None):
        with open("streetview/data/missing_link_direction.json", "r") as f:
            return json.load(f)

    streetview.api.find_panorama_by_id_raw = mocked_find_panorama_by_id_raw

    pano = streetview.find_panorama_by_id("VAhJEVyAlZg-QgAnUwcIRA")
    assert pano.links[0].direction == approx(0.07641416505750565)


def test_places():
    def mocked_find_panorama_by_id_raw(panoid, download_depth=False, locale="en", session=None):
        with open("streetview/data/places.json", "r") as f:
            return json.load(f)

    streetview.api.find_panorama_by_id_raw = mocked_find_panorama_by_id_raw

    pano = streetview.find_panorama_by_id("gjDG9WfyVFri9OT0A4LaWw")
    assert len(pano.places) == 3
    assert pano.places[2].name.value == 'Old Parliament House'
    assert pano.places[2].type.value == 'Museum'
    assert pano.places[2].feature_id == '0x6b164d18e0254b09:0x4ec7b2ac1171a085'
    assert pano.places[2].marker_yaw == approx(1.6297568407941114)
    assert pano.places[2].marker_pitch == approx(-0.00047187885564841503)
    assert pano.places[2].marker_distance == approx(29.35295486450195)
