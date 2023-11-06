from pytest import approx
import json
from streetlevel import streetside


def mocked_api_find_panoramas(north, west, south, east, limit=50, session=None):
    with open("streetside/data/find.json", "r") as f:
        return json.load(f)


streetside.api.find_panoramas = mocked_api_find_panoramas


def test_find_panoramas_in_bbox():
    panos = streetside.find_panoramas_in_bbox(-23.860792, 35.343169, -23.863089, 35.347470)
    assert len(panos) != 0
    assert panos[0].id == 362530254
    assert panos[0].lat == approx(-23.862083, 0.001)
    assert panos[0].lon == approx(35.34479, 0.001)


def test_to_base4():
    assert streetside.to_base4(6) == "12"


def test_from_base4():
    assert streetside.from_base4("12") == 6
