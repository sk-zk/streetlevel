from datetime import datetime
from pytest import approx

from streetlevel import lookaround
from streetlevel.lookaround.proto import GroundMetadataTile_pb2


def test_get_coverage_tile():
    def mocked_get_coverage_tile(tile_x, tile_y, session=None):
        with open("lookaround/data/metadata_tile.pb", "rb") as f:
            tile_pb = f.read()
        tile = GroundMetadataTile_pb2.GroundMetadataTile()
        tile.ParseFromString(tile_pb)
        return tile
    lookaround.api.get_coverage_tile = mocked_get_coverage_tile

    panos = lookaround.get_coverage_tile_by_latlon(37.793871595174096, -122.43653154373168)
    assert panos[0].id == 8227292017329697463
    assert panos[0].build_id == 1392282981
    assert panos[0].date == datetime(2022, 4, 2, 22, 14, 21, 111000)
    assert panos[0].coverage_type == lookaround.CoverageType.CAR
    assert panos[0].heading == approx(1.7832050655066374)
    assert panos[0].pitch == approx(-0.016837476195331824)
    assert panos[0].roll == approx(-0.030182552495642945)
    assert panos[0].elevation == approx(80.48369275437446)
