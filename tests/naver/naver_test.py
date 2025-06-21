from datetime import datetime
import json

from pytest import approx

from streetlevel import naver
import streetlevel.naver.parse
from streetlevel.naver.panorama import PanoramaType


def test_parse_panorama():
    with open("naver/data/find_by_id.json", "r") as f:
        response = json.load(f)

    pano = naver.parse.parse_panorama(response)
    assert pano.id == "FkJFCbuLmOnbKvHME1QNmw"
    assert pano.lat == approx(37.5742511)
    assert pano.lon == approx(126.9829791)
    assert pano.heading == approx(3.081290326852233)
    assert pano.pitch == approx(-0.011458714437974749)
    assert pano.roll == approx(0.007665953426398905)
    assert pano.altitude == approx(58.44)
    assert pano.is_latest
    assert pano.date == datetime(2025, 3, 25, 11, 8, 47)
    assert pano.has_equirect
    assert pano.panorama_type == PanoramaType.MESH_EQUIRECT


def test_parse_nearby():
    with open("naver/data/find.json", "r") as f:
        response = json.load(f)

    pano = naver.parse.parse_nearby(response)
    assert pano.id == "FkJFCbuLmOnbKvHME1QNmw"
    assert pano.lat == approx(37.5742511)
    assert pano.lon == approx(126.9829791)
    assert pano.heading == approx(-0.0603883921190038)
    assert pano.altitude == approx(58.44)
    assert pano.date == datetime(2025, 3, 25, 11, 8, 47)
