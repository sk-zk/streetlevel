import pytest
from pytest import approx
import pickle
from streetlevel import mapy
from streetlevel.dataclasses import Size


def mocked_getbest(lat, lon, radius, options=None):
    with open("mapy/data/getbest.pkl", "rb") as f:
        return pickle.load(f)


mapy.api.getbest = mocked_getbest


def test_find_panorama():
    pano = mapy.find_panorama(50.1265193, 17.3762701, 100.0, historical=False, links=False)
    assert pano.id == 59418543
    assert pano.lat == approx(50.1265193, 0.001)
    assert pano.lon == approx(17.3762701, 0.001)
    assert pano.provider == "stavinvex"
    assert pano.num_tiles == [Size(x=1, y=1), Size(x=16, y=8)]
    assert pano.pitch == approx(0.01970877694733808, 0.001)
    assert pano.roll == approx(0.019988022665593075, 0.001)
