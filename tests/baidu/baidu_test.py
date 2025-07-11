from datetime import datetime, timezone, timedelta
import json

from pytest import approx

from streetlevel import baidu
import streetlevel.baidu.parse
from streetlevel.baidu.panorama import Provider


def test_parse_panorama_response():
    with open("baidu/data/find.json", "r") as f:
        response = json.load(f)

    pano = baidu.parse.parse_panorama_response(response)
    assert pano.id == "0900030012221106110957982GC"
    assert pano.x == approx(13525966.27)
    assert pano.y == approx(3639126.52)
    assert pano.elevation == approx(16.38)
    assert pano.lat == approx(31.2173354778762)
    assert pano.lon == approx(121.49345589207972)
    assert pano.gcj02_lat == approx(31.215315881785134)
    assert pano.gcj02_lon == approx(121.49789346245744)
    assert pano.heading == approx(0.6632251157578453)
    assert pano.pitch == approx(0.08080874436733745)
    assert pano.roll == approx(-0.010471975511965976)
    assert pano.date == datetime(2022, 11, 6, 11, 9, 57,
                                 tzinfo=timezone(timedelta(hours=8), "Asia/Shanghai"))
    assert pano.provider == Provider.BAIDU
