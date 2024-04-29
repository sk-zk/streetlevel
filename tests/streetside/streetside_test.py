from pytest import approx
import json

from streetlevel import streetside
import streetlevel.streetside.parse


def test_parse_panoramas():
    with open("streetside/data/find.json", "r") as f:
        response = json.load(f)

    panos = streetside.parse.parse_panoramas(response)
    assert len(panos) != 0
    assert panos[0].id == 362530254
    assert panos[0].lat == approx(-23.862083, 0.001)
    assert panos[0].lon == approx(35.34479, 0.001)


def test_to_base4():
    assert streetside.to_base4(6) == "12"


def test_from_base4():
    assert streetside.from_base4("12") == 6
