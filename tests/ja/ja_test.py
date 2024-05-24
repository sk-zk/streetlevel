from pytest import approx
import json

from streetlevel import ja
import streetlevel.ja.parse


def test_parse_panorama_radius_response():
    with open("ja/data/find.json", "r") as f:
        response = json.load(f)

    pano = ja.parse.parse_panorama_radius_response(response)
    assert pano.id == 2421456
    assert pano.lat == approx(64.135776)
    assert pano.lon == approx(-21.860711)
    assert pano.heading == approx(0.606676)


def test_parse_panorama_id_response():
    with open("ja/data/find_by_id.json", "r") as f:
        response = json.load(f)

    pano = ja.parse.parse_panorama_id_response(response)
    assert pano.id == 2421455
    assert pano.lat == approx(64.135729)
    assert pano.lon == approx(-21.860767)
    assert pano.heading == approx(0.591492)
    assert pano.date.year == 2022
    assert pano.date.month == 7
    assert len(pano.neighbors) == 59
    assert pano.street_names[0].name == "Goðheimar"