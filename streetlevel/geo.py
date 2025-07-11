import math
from typing import Tuple

import pyproj
from pyproj import Transformer
from scipy.spatial.transform import Rotation
import bd09convertor
import CoordinatesConverter


pyproj.network.set_network_enabled(active=True)
_geod = pyproj.Geod(ellps="WGS84")
_tf_wgs84_to_wgs84_egm2008 = Transformer.from_crs(4979, 9518)
_tf_wgs84_to_isn93 = Transformer.from_crs(4326, 3057)


def tile_coord_to_wgs84(x: float, y: float, zoom: int) -> Tuple[float, float]:
    """
    Converts XYZ tile coordinates to WGS84 coordinates.

    :param x: X coordinate.
    :param y: Y coordinate.
    :param zoom: Z coordinate.
    :return: WGS84 coordinates.
    """
    scale = 1 << zoom
    lon_deg = x / scale * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / scale)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg
    

def wgs84_to_tile_coord(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
    """
    Converts WGS84 coordinates to XYZ coordinates.

    :param lat: Latitude.
    :param lon: Longitude.
    :param zoom: Z coordinate.
    :return: The X and Y coordinates.
    """
    lat_rad = math.radians(lat)
    scale = 1 << zoom
    x = (lon + 180.0) / 360.0 * scale
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * scale
    return int(x), int(y)


def wgs84_to_isn93(lat: float, lon: float) -> Tuple[float, float]:
    """
    Converts WGS84 coordinates to ISN93 coordinates.

    :param lat: Latitude.
    :param lon: Longitude.
    :return: ISN93 coordinates.
    """
    return _tf_wgs84_to_isn93.transform(lat, lon)


def wgs84_to_bd09mc(lat: float, lon: float) -> Tuple[float, float]:
    """
    Converts WGS84 coordinates to BD09 Mercator coordinates.

    :param lat: Latitude.
    :param lon: Longitude.
    :return: BD09 Mercator coordinates.
    """
    bd09 = CoordinatesConverter.wgs84tobd09(lon, lat)
    return bd09convertor.convertLL2MC(bd09[0], bd09[1])


def bd09_to_bd09mc(lat: float, lon: float) -> Tuple[float, float]:
    """
    Converts BD09 coordinates to BD09 Mercator coordinates.

    :param lat: Latitude.
    :param lon: Longitude.
    :return: BD09 Mercator coordinates.
    """
    return bd09convertor.convertLL2MC(lon, lat)


def gcj02_to_bd09mc(lat: float, lon: float) -> Tuple[float, float]:
    """
    Converts GCJ-02 coordinates to BD09 Mercator coordinates.

    :param lat: Latitude.
    :param lon: Longitude.
    :return: BD09 Mercator coordinates.
    """
    bd09 = CoordinatesConverter.gcj02tobd09(lon, lat)
    return bd09convertor.convertLL2MC(bd09[0], bd09[1])


def bd09mc_to_wgs84(x: float, y: float) -> Tuple[float, float]:
    """
    Converts BD09 Mercator coordinates to WGS84 coordinates.

    :param x: X coordinate.
    :param y: Y coordinate.
    :return: WGS84 coordinates.
    """
    bd09 = bd09convertor.convertMC2LL(x, y)
    wgs = CoordinatesConverter.bd09towgs84(bd09[0], bd09[1])
    return wgs[1], wgs[0]


def bd09mc_to_gcj02(x: float, y: float) -> Tuple[float, float]:
    """
    Converts BD09 Mercator coordinates to GCJ-02 coordinates.

    :param x: X coordinate.
    :param y: Y coordinate.
    :return: GCJ-02 coordinates.
    """
    bd09 = bd09convertor.convertMC2LL(x, y)
    gcj = CoordinatesConverter.bd09togcj02(bd09[0], bd09[1])
    return gcj[1], gcj[0]


def create_bounding_box_around_point(lat: float, lon: float, radius: float) \
        -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Creates a square bounding box around a point.

    :param lat: Latitude of the center point.
    :param lon: Longitude of the center point.
    :param radius: Shortest distance from the center point to the edges of the square.
    :return: Latitude and longitude of the NW and SE points.
    """
    dist_to_corner = math.sqrt(2 * pow(2 * radius, 2)) / 2
    lon1, lat1, _ = _geod.fwd(lon, lat, 315, dist_to_corner)
    top_left = lat1, lon1
    lon2, lat2, _ = _geod.fwd(lon, lat, 135, dist_to_corner)
    bottom_right = lat2, lon2
    return top_left, bottom_right


def opk_to_rotation(omega: float, phi: float, kappa: float) -> Rotation:
    """
    Creates a SciPy rotation object from omega/phi/kappa angles.
    """
    return Rotation.from_euler('zxy', [phi, -omega, kappa])


def get_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns the bearing from point 1 to point 2.

    :param lat1: Latitude of point 1.
    :param lon1: Longitude of point 2.
    :param lat2: Latitude of point 2.
    :param lon2: Longitude of point 2.
    :return: The bearing in radians.
    """
    fwd_azimuth, _, _ = _geod.inv(lon1, lat1, lon2, lat2)
    return math.radians(fwd_azimuth)


def get_geoid_height(lat: float, lon: float) -> float:
    """
    Returns the EGM2008 geoid height at a WGS84 coordinate.

    :param lat: Latitude.
    :param lon: Longitude.
    :return: Geoid height in meters.
    """
    _, _, geoid_height = _tf_wgs84_to_wgs84_egm2008.transform(lat, lon, 0)
    return -geoid_height
