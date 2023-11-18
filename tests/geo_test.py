import math

from pytest import approx
from streetlevel import geo


def test_wgs84_to_tile_coord():
    expected = (69172, 42368)
    actual = geo.wgs84_to_tile_coord(53.539043721545404, 9.98702908360777, 17)
    assert expected == actual


def tile_coord_to_wgs84():
    expected = (53.54030739150021, 9.986572265625)
    actual = geo.tile_coord_to_wgs84(69172, 42368, 17)
    assert actual[0] == approx(expected[0], 0.00001)
    assert actual[1] == approx(expected[1], 0.00001)


def test_wgs84_to_isn93():
    lat, lon = 63.626878, -19.635691
    expected = 468474.712568, 347078.460339
    actual = geo.wgs84_to_isn93(lat, lon)
    assert actual[0] == approx(expected[0])
    assert actual[1] == approx(expected[1])


def test_get_bearing():
    lat1, lon1 = 56.4022257183309, 10.419846839556701
    lat2, lon2 = 56.493210323925524, 10.6829783303312
    expected = 1.0107660582679734
    actual = geo.get_bearing(lat1, lon1, lat2, lon2)
    assert actual == approx(expected)


def test_get_geoid_height():
    lat, lon = -41.374063214267025, 146.26566929883762
    expected = -1.354967
    actual = geo.get_geoid_height(lat, lon)
    assert actual == approx(expected)
