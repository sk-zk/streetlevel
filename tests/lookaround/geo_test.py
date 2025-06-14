from pytest import approx
from streetlevel.lookaround.geo import protobuf_tile_offset_to_wgs84, convert_altitude, convert_pano_orientation


def test_protobuf_tile_offset_to_wgs84():
    x_offset, y_offset = 11908, 272
    tile_x, tile_y = 63184, 43094
    expected_lat, expected_lon = 52.33704527861042, -6.457956875071801
    actual_lat, actual_lon = protobuf_tile_offset_to_wgs84(x_offset, y_offset, tile_x, tile_y)
    assert actual_lat == approx(expected_lat)
    assert actual_lon == approx(expected_lon)


def test_convert_altitude():
    raw_altitude = 5268
    lat, lon = 52.33704527861042, -6.457956875071801
    tile_x, tile_y = 63184, 43094
    expected_altitude, expected_elevation = 60.20049267872333, 3.8995043053279588
    actual_altitude, actual_elevation = convert_altitude(raw_altitude, lat, lon, tile_x, tile_y)
    assert actual_altitude == approx(expected_altitude)
    assert actual_elevation == approx(expected_elevation)


def test_convert_pano_orientation():
    lat, lon = 52.33704527861042, -6.457956875071801
    raw_yaw, raw_pitch, raw_roll = 1669, 1377, 9363
    expected_yaw, expected_pitch, expected_roll = 0.6318033516997712, -0.013740416000112887, -0.018287546853410053
    actual_yaw, actual_pitch, actual_roll = convert_pano_orientation(lat, lon, raw_yaw, raw_pitch, raw_roll)
    assert actual_yaw == approx(expected_yaw)
    assert actual_pitch == approx(expected_pitch)
    assert actual_roll == approx(expected_roll)
