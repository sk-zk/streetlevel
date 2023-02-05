# based on
# https://stackoverflow.com/a/56245973
# by ted, CC BY-SA 4.0
# which is derived from
# https://github.com/proog128/GSVPanoDepth.js
# by proog128, MIT

import base64
import numpy as np
import struct

from streetlevel.streetview.panorama import DepthMap

INFINITELY_FAR = -1


def parse(b64_string: str) -> DepthMap:
    raw_data = decode_b64(b64_string)
    header = parse_header(raw_data)
    planes = parse_planes(header, raw_data)
    depth_map = compute_depth_map(header, planes["planes"], planes["indices"])
    depth_map["data"] = depth_map["data"].reshape((depth_map["height"], depth_map["width"]))
    return DepthMap(depth_map["width"], depth_map["height"], depth_map["data"])


def decode_b64(b64_string: str) -> np.ndarray:
    b64_string += "=" * ((4 - len(b64_string) % 4) % 4)  # add padding if necessary
    data = base64.urlsafe_b64decode(b64_string)
    return np.array([d for d in data])


def parse_header(depth_map):
    return {
        "header_size": depth_map[0],
        "number_of_planes": get_uint16(depth_map, 1),
        "width": get_uint16(depth_map, 3),
        "height": get_uint16(depth_map, 5),
        "offset": get_uint16(depth_map, 7),
    }


def get_bin(a):
    ba = bin(a)[2:]
    return "0" * (8 - len(ba)) + ba


def get_uint16(arr, ind):
    a = arr[ind]
    b = arr[ind + 1]
    return int(get_bin(b) + get_bin(a), 2)


def get_float(arr, ind):
    return bin_to_float("".join(get_bin(i) for i in arr[ind: ind + 4][::-1]))


def bin_to_float(binary):
    return struct.unpack("!f", struct.pack("!I", int(binary, 2)))[0]


def parse_planes(header, depth_map):
    indices = []
    planes = []

    for i in range(header["width"] * header["height"]):
        indices.append(depth_map[header["offset"] + i])

    for i in range(header["number_of_planes"]):
        byte_offset = header["offset"] + header["width"] * header["height"] + i * 4 * 4
        n = [0, 0, 0]
        n[0] = get_float(depth_map, byte_offset)
        n[1] = get_float(depth_map, byte_offset + 4)
        n[2] = get_float(depth_map, byte_offset + 8)
        d = get_float(depth_map, byte_offset + 12)
        planes.append({"n": n, "d": d})

    return {"planes": planes, "indices": indices}


def compute_depth_map(header, planes, indices):
    v = [0, 0, 0]
    w = header["width"]
    h = header["height"]

    depth_map = np.empty(w * h)

    sin_theta = np.empty(h)
    cos_theta = np.empty(h)
    sin_phi = np.empty(w)
    cos_phi = np.empty(w)

    for y in range(h):
        theta = (h - y - 0.5) / h * np.pi
        sin_theta[y] = np.sin(theta)
        cos_theta[y] = np.cos(theta)

    for x in range(w):
        phi = (w - x - 0.5) / w * 2 * np.pi + np.pi / 2
        sin_phi[x] = np.sin(phi)
        cos_phi[x] = np.cos(phi)

    for y in range(h):
        for x in range(w):
            plane_idx = indices[y * w + x]

            v[0] = sin_theta[y] * cos_phi[x]
            v[1] = sin_theta[y] * sin_phi[x]
            v[2] = cos_theta[y]

            if plane_idx > 0:
                plane = planes[plane_idx]
                t = np.abs(
                    plane["d"] / (
                            v[0] * plane["n"][0]
                            + v[1] * plane["n"][1]
                            + v[2] * plane["n"][2]
                    )
                )
                depth_map[y * w + (w - x - 1)] = t
            else:
                depth_map[y * w + (w - x - 1)] = INFINITELY_FAR
    return {"width": w, "height": h, "data": depth_map}
