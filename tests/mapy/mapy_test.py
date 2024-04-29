import pytest
from pytest import approx
import pickle

from streetlevel import mapy
import streetlevel.mapy.parse
from streetlevel.dataclasses import Size


def test_parse_getbest_response():
    with open("mapy/data/getbest.pkl", "rb") as f:
        response = pickle.load(f)

    pano = mapy.parse.parse_getbest_response(response)
    assert pano.id == 59418543
    assert pano.lat == approx(50.1265193, 0.001)
    assert pano.lon == approx(17.3762701, 0.001)
    assert pano.provider == "stavinvex"
    assert pano.num_tiles == [Size(x=1, y=1), Size(x=16, y=8)]
    assert pano.pitch == approx(0.01970877694733808, 0.001)
    assert pano.roll == approx(0.019988022665593075, 0.001)
