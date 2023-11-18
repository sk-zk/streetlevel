from datetime import datetime

from pytest import approx
import json

from requests import Session

from streetlevel import yandex


def mocked_api_find_panorama(lat: float, lon: float, session: Session = None) -> dict:
    with open("yandex/data/find.json", "r") as f:
        return json.load(f)


yandex.api.find_panorama = mocked_api_find_panorama


def test_find_panorama():
    pano = yandex.find_panorama(53.917633, 27.548128)
    assert pano.id == "1238072810_692204477_23_1688105969"
    assert pano.lat == approx(53.917633, 0.001)
    assert pano.lon == approx(27.548128, 0.001)
    assert pano.date == datetime.utcfromtimestamp(1688105969)
    assert pano.image_id == "WhpeuZGm2FIL"
    assert pano.image_sizes[0].x == 17664
    assert pano.image_sizes[0].y == 6145
