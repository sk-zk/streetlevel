import math
import pyproj
from scipy.spatial.transform import Rotation

TILE_SIZE = 256
geod = pyproj.Geod(ellps="WGS84")


def mercator_to_wgs84(x, y):
    lat = (2 * math.atan(math.exp((y - 128) / -(256 / (2 * math.pi)))) - math.pi / 2) / (math.pi / 180)
    lon = (x - 128) / (256 / 360)
    return lat, lon


def tile_coord_to_wgs84(x, y, zoom):
    scale = 1 << zoom
    pixel_coord = (x * TILE_SIZE, y * TILE_SIZE)
    world_coord = (pixel_coord[0] / scale, pixel_coord[1] / scale)
    lat_lon = mercator_to_wgs84(world_coord[0], world_coord[1])
    return lat_lon[1], lat_lon[0]
    

def wgs84_to_tile_coord(lat, lon, zoom):
    scale = 1 << zoom
    world_coord = wgs84_to_mercator(lat, lon)
    pixel_coord = (math.floor(world_coord[0] * scale), math.floor(world_coord[1] * scale))
    tile_coord = (math.floor((world_coord[0] * scale) / TILE_SIZE), math.floor((world_coord[1] * scale) / TILE_SIZE))
    return tile_coord


def wgs84_to_mercator(lat, lon):
    siny = math.sin((lat * math.pi) / 180.0)
    siny = min(max(siny, -0.9999), 0.9999)
    return (
        TILE_SIZE * (0.5 + lon / 360.0),
        TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
    )


def create_bounding_box_around_point(lat, lon, radius):
    dist_to_corner = math.sqrt(2 * pow(2 * radius, 2)) / 2
    top_left = geod.fwd(lon, lat, 315, dist_to_corner)
    bottom_right = geod.fwd(lon, lat, 135, dist_to_corner)
    return top_left, bottom_right


def opk_to_rotation(omega: float, phi: float, kappa: float) -> Rotation:
    """
    Creates a SciPy rotation object from omega/phi/kappa angles.
    """
    return Rotation.from_euler('zxy', [phi, -omega, kappa])
