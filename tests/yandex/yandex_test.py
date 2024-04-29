from datetime import datetime
import json

from pytest import approx

from streetlevel import yandex
import streetlevel.yandex.parse


def test_parse_panorama_response():
    with open("yandex/data/find.json", "r") as f:
        response = json.load(f)

    pano = yandex.parse.parse_panorama_response(response)
    assert pano.id == "1238072810_692204477_23_1688105969"
    assert pano.lat == approx(53.917633, 0.001)
    assert pano.lon == approx(27.548128, 0.001)
    assert pano.date == datetime.utcfromtimestamp(1688105969)
    assert pano.image_id == "WhpeuZGm2FIL"
    assert pano.image_sizes[0].x == 17664
    assert pano.image_sizes[0].y == 6145
