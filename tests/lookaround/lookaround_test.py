from datetime import datetime, timezone
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
    assert panos[0].date == datetime(2022, 4, 2,
                                     22, 14, 21, 111000,
                                     timezone.utc)
    assert panos[0].coverage_type == CoverageType.CAR
    assert panos[0].heading == approx(1.7832923433779566)
    assert panos[0].pitch == approx(0.03305357743988524)
    assert panos[0].roll == approx(-0.010094509175066158)
    assert panos[0].elevation == approx(80.48369275437446)
