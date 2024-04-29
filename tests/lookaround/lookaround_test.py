from datetime import datetime
from pytest import approx

from streetlevel import lookaround
from streetlevel.lookaround.proto import GroundMetadataTile_pb2
from streetlevel.lookaround.panorama import CoverageType
import streetlevel.lookaround.parse


def test_parse_coverage_tile():
    with open("lookaround/data/metadata_tile.pb", "rb") as f:
        tile_pb = f.read()
    tile = GroundMetadataTile_pb2.GroundMetadataTile()
    tile.ParseFromString(tile_pb)

    panos = lookaround.parse.parse_coverage_tile(tile)
    assert panos[0].id == 8227292017329697463
    assert panos[0].build_id == 1392282981
    assert panos[0].date == datetime(2022, 4, 2, 22, 14, 21, 111000)
    assert panos[0].coverage_type == CoverageType.CAR
    assert panos[0].heading == approx(1.7832050655066374)
    assert panos[0].pitch == approx(-0.016837476195331824)
    assert panos[0].roll == approx(-0.030182552495642945)
    assert panos[0].elevation == approx(80.48369275437446)
