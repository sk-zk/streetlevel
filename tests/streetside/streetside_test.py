import pytest
from pytest import approx
import json
from streetlevel import streetside
from streetlevel.dataclasses import Size


def mocked_find_panoramas_raw(north, west, south, east, limit=50, session=None):
    with open("streetside/data/find_object.json", "r") as f:
        return json.load(f)


streetside.streetside._find_panoramas_raw = mocked_find_panoramas_raw


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