from datetime import datetime
import json

from pytest import approx

from streetlevel import kakao
import streetlevel.kakao.parse

def test_parse_panoramas():
    with open("kakao/data/find.json", "r") as f:
        response = json.load(f)

    panos = kakao.parse.parse_panoramas(response)
    assert len(panos) == 10
    assert panos[0].id == 1196290584
    assert panos[0].wcongx == approx(1358803.0)
    assert panos[0].wcongy == approx(1121615.0)
    assert panos[0].lat == approx(37.4734586415908)
    assert panos[0].lon == approx(130.882715794065)
    assert panos[0].heading == approx(5.218534463463046)
    assert panos[0].image_path == "/2025/04/9147464/2_100060_9147464_20250421214948"
    assert panos[0].date == datetime(2025, 4, 21, 21, 49, 48)


def test_parse_panorama():
    with open("kakao/data/find_by_id.json", "r") as f:
        response = json.load(f)

    pano = kakao.parse.parse_panorama(response["street_view"]["street"])
    assert pano.id == 1196290584
    assert pano.wcongx == approx(1358803.0)
    assert pano.wcongy == approx(1121615.0)
    assert pano.lat == approx(37.4734586415908)
    assert pano.lon == approx(130.882715794065)
    assert pano.heading == approx(5.218534463463046)
    assert pano.image_path == "/2025/04/9147464/2_100060_9147464_20250421214948"
    assert pano.date == datetime(2025, 4, 21, 21, 49, 48)

    assert len(pano.historical) == 2
    assert len(pano.links) == 2
    assert pano.neighbors is None
