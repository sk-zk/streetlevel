from datetime import datetime, timezone
from typing import List

from streetlevel.lookaround.geo import protobuf_tile_offset_to_wgs84
from streetlevel.lookaround.panorama import LookaroundPanorama, CoverageType, LensProjection, CameraMetadata, \
    OrientedPosition
from streetlevel.lookaround.proto import GroundMetadataTile_pb2


def parse_coverage_tile(tile: GroundMetadataTile_pb2.GroundMetadataTile) \
        -> List[LookaroundPanorama]:
    panos = []
    camera_metadatas = [_camera_metadata_to_dataclass(c) for c in tile.camera_metadata]
    for pano_pb in tile.pano:
        lat, lon = protobuf_tile_offset_to_wgs84(
            pano_pb.tile_position.x,
            pano_pb.tile_position.y,
            tile.tile_coordinate.x,
            tile.tile_coordinate.y)
        pano = LookaroundPanorama(
            id=pano_pb.panoid,
            build_id=tile.build_table[pano_pb.build_table_idx].build_id,
            lat=lat,
            lon=lon,
            coverage_type=CoverageType(tile.build_table[pano_pb.build_table_idx].coverage_type),
            date=datetime.fromtimestamp(pano_pb.timestamp / 1000.0, timezone.utc),
            has_blurs=tile.build_table[pano_pb.build_table_idx].index != 0,
            raw_orientation=(pano_pb.tile_position.yaw, pano_pb.tile_position.pitch, pano_pb.tile_position.roll),
            raw_altitude=pano_pb.tile_position.altitude,
            tile=(tile.tile_coordinate.x, tile.tile_coordinate.y, tile.tile_coordinate.z),
            camera_metadata=[camera_metadatas[i] for i in pano_pb.camera_metadata_idx]
        )
        panos.append(pano)
    return panos


def _camera_metadata_to_dataclass(camera_metadata_pb: GroundMetadataTile_pb2.CameraMetadata):
    lens_projection_pb = camera_metadata_pb.lens_projection
    position_pb = camera_metadata_pb.position
    return CameraMetadata(
        lens_projection=LensProjection(
            fov_s=lens_projection_pb.fov_s,
            fov_h=lens_projection_pb.fov_h,
            k2=lens_projection_pb.k2,
            k3=lens_projection_pb.k3,
            k4=lens_projection_pb.k4,
            cx=lens_projection_pb.cx,
            cy=lens_projection_pb.cy,
            lx=lens_projection_pb.lx,
            ly=lens_projection_pb.ly,
        ),
        position=OrientedPosition(
            x=position_pb.x,
            y=position_pb.y,
            z=position_pb.z,
            yaw=position_pb.yaw,
            pitch=position_pb.pitch,
            roll=position_pb.roll,
        )
    )
