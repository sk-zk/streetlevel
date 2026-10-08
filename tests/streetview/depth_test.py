import base64
import math
import struct

from pytest import approx

from streetlevel.streetview import depth


def build_depth_map(width, height, planes, plane_indices):
    """Assemble a depth map in the documented layout.

    Header is eight bytes: a header size, then three uint16 fields, then the offset at
    which the plane indices begin. The index array follows, then the planes, each a
    little-endian normal and distance.
    """
    header = (bytes([8])
              + struct.pack("<HHH", len(planes), width, height)
              + bytes([8]))
    indices = bytes(plane_indices)
    plane_data = b"".join(struct.pack("<ffff", *plane) for plane in planes)
    raw = header + indices + plane_data
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


GROUND = (0.0, 0.0, -1.0, 2.5)
WALL = (1.0, 0.0, 0.0, 10.0)

# Bottom row of a four-row map is centred 22.5 degrees off the nadir, so a ray to the
# ground plane is 2.5 / cos(22.5 degrees) long.
BOTTOM_ROW_DEPTH = 2.5 / math.cos(math.radians(22.5))


def test_parse_header():
    depth_map = build_depth_map(8, 4, [GROUND, GROUND], [0] * 32)
    header = depth.parse_header(depth.decode_b64(depth_map))

    assert header["header_size"] == 8
    assert header["number_of_planes"] == 2
    assert header["width"] == 8
    assert header["height"] == 4
    assert header["offset"] == 8


def test_parse_with_sky_as_first_plane_index():
    depth_map = build_depth_map(8, 4, [GROUND, GROUND], [0] * 16 + [1] * 16)
    parsed = depth.parse(depth_map)

    assert parsed.width == 8
    assert parsed.height == 4
    assert parsed.data[0][0] == depth.INFINITELY_FAR
    assert parsed.data[3][0] == approx(BOTTOM_ROW_DEPTH, rel=1e-6)


def test_parse_with_nonzero_first_plane_index():
    """The first plane index sits at byte 8, immediately after the eight-byte header.

    Reading the offset field as a uint16 consumes that byte as a high byte, so the
    offset comes out as 8 + 256 * first_index instead of 8. It is only correct when the
    top left pixel happens to be sky, and otherwise the plane list is read past the end
    of the buffer and parsing raises. Here the top half is a wall, so the first index is
    2 rather than 0.
    """
    depth_map = build_depth_map(8, 4, [GROUND, GROUND, WALL], [2] * 16 + [1] * 16)
    parsed = depth.parse(depth_map)

    assert parsed.width == 8
    assert parsed.height == 4
    assert parsed.data[3][0] == approx(BOTTOM_ROW_DEPTH, rel=1e-6)
