from datetime import datetime, timezone

from pytest import approx, raises
import json
from streetlevel import streetview
from streetlevel.dataclasses import Size
import streetlevel.streetview.parse


def test_is_third_party_panoid():
    assert not streetview.is_third_party_panoid("n-Zd6bDDL_XOc_jkNgFsGg")
    assert streetview.is_third_party_panoid("AF1QipN3bwjvnpTUbfCZ18wsUMrpZ6Ul2mhVfNKl71_X")


def test_find_panorama_by_id():
    with open("streetview/data/find_by_id.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert pano.id == "n-Zd6bDDL_XOc_jkNgFsGg"
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)
    assert pano.date.month == 3
    assert pano.date.year == 2021
    assert pano.country_code == "AT"
    assert pano.tile_size == Size(512, 512)
    assert len(pano.image_sizes) == 6
    assert pano.image_sizes[-1] == Size(16384, 8192)


def test_find_panorama():
    with open("streetview/data/find.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_radius_response(response)
    assert pano.id == "n-Zd6bDDL_XOc_jkNgFsGg"
    assert pano.lat == approx(47.15048822721601, 0.001)
    assert pano.lon == approx(11.13385612403307, 0.001)


def test_find_get_coverage_tile_by_latlon():
    with open("streetview/data/coverage_tile.json", "r") as f:
        response = json.load(f)

    panos = streetview.parse.parse_coverage_tile_response(response)
    assert any(p.id == "n-Zd6bDDL_XOc_jkNgFsGg" for p in panos)


def test_nepal_links():
    with open("streetview/data/nepal_links.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert pano.links[0].pano.id == "yCIEQ7o37R49IxNPOkhWgw"
    assert pano.links[0].pano.lat is None
    assert pano.links[1].pano.id == "C9aepLhvgmFjRJlP2GxjXQ"
    assert pano.links[1].pano.lat is None


def test_missing_link_direction():
    with open("streetview/data/missing_link_direction.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert pano.links[0].direction == approx(0.07641416505750565)


def test_places():
    with open("streetview/data/places.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert len(pano.places) == 3
    assert pano.places[2].name.value == "Old Parliament House"
    assert pano.places[2].type.value == "Museum"
    assert pano.places[2].feature_id == "0x6b164d18e0254b09:0x4ec7b2ac1171a085"
    assert pano.places[2].cid == 5676702307420577925
    assert pano.places[2].marker_yaw == approx(1.6297568407941114)
    assert pano.places[2].marker_pitch == approx(-0.00047187885564841503)
    assert pano.places[2].marker_distance == approx(29.35295486450195)


def test_missing_level_name():
    with open("streetview/data/missing_level_name.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert pano.building_level is not None
    assert pano.building_level.level == 0
    assert pano.building_level.name is None
    assert pano.building_level.short_name is None
    

def test_missing_date():
    with open("streetview/data/missing_date.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert pano.date is None


def test_missing_historical_date():
    with open("streetview/data/missing_historical_date.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)
    assert pano.date.year == 2017
    assert pano.date.month == 7
    assert len(pano.historical) == 1
    assert pano.historical[0].id == "ZvY4uyCZ7BkAAARDoyHfCA"
    assert pano.historical[0].date is None


def test_street_names():
    def mocked_api_find_panorama_by_id(panoid, download_depth=False, locale="en", session=None):
        with open("streetview/data/street_names.json", "r") as f:
            return json.load(f)
    
    streetview.api.find_panorama_by_id = mocked_api_find_panorama_by_id

    pano = streetview.find_panorama_by_id('BoiJ2WQ2FM7Rr9UjcGqK8w')
    assert pano is not None
    assert pano.street_names is not None
    assert len(pano.street_names) == 2
    assert pano.street_names[0].name.value == "Benjamin Way"
    assert len(pano.street_names[0].angles) == 2
    assert pano.street_names[0].angles[0] == approx(0.5802275672274712)
    assert pano.street_names[0].angles[1] == approx(3.980519023317289)
    assert pano.street_names[1].name.value == "Belconnen Way"
    assert len(pano.street_names[1].angles) == 2
    assert pano.street_names[1].angles[0] == approx(1.949208880825891)
    assert pano.street_names[1].angles[1] == approx(5.04117805487591)


def test_build_permalink_raises():
    with raises(ValueError):
        streetview.build_permalink(lat=42, lon=None)
    with raises(ValueError):
        streetview.build_permalink(lat=None, lon=42)
    with raises(ValueError):
        streetview.build_permalink()


def test_get_exact_datetime_if_available():
    # field 12 contains UUID - use regular date field instead
    with open("streetview/data/ari_with_uuid_in_12.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)

    assert pano.date.year == 2022
    assert pano.date.month == 10
    assert pano.date.day == 9

    # field 12 contains timestamp
    with open("streetview/data/ari_with_timestamp_in_12.json", "r") as f:
        response = json.load(f)

    pano = streetview.parse.parse_panorama_id_response(response)

    assert pano.date == datetime(2024, 8, 5,
                                 5, 53, 6, 769000,
                                 tzinfo=timezone.utc)
