import math
from typing import List

from PIL import Image
from equilib import Equi2Equi
import torch
from torchvision import transforms

from streetlevel.lookaround import CameraMetadata

_equi2equi = Equi2Equi(mode="bilinear", z_down=True)
_device = torch.device("cuda")
_to_tensor = transforms.Compose([transforms.ToTensor()])
_to_pil = transforms.Compose([transforms.ToPILImage()])


def to_equirectangular(faces: List[Image.Image], camera_metadata: List[CameraMetadata]) -> Image.Image:
    """
    Reprojects the faces of a Look Around panorama to a single equirectangular image. The center of the
    returned image is the inverse direction of travel (meaning you're looking backwards).

    Note that this method is *very* slow. On my machine, a full resolution image (zoom 0, 16384×8192) takes
    about 50 seconds to convert.

    **PyTorch must be installed** to call this function. Due to its size and differing CUDA versions,
    it is not installed automatically alongside the other dependencies of this library.

    :param faces: The faces of the panorama as PIL images.
    :param camera_metadata: The camera metadata of the faces.
    :return: The reprojected panorama as PIL image.
    """
    full_width = round(faces[0].width * (1024 / 5632)) * 16
    full_height = full_width // 2

    stitched = Image.new("RGB", (full_width, full_height))

    for faceIndex in range(5, -1, -1):
        if faceIndex > 3:
            projected = _project_top_or_bottom_face(
                faces[faceIndex], camera_metadata[faceIndex], full_width, full_height)
            stitched.paste(projected, (0, 0), projected)
        else:
            _paste_side_face(faces[faceIndex], camera_metadata[faceIndex], full_width, full_height, stitched)
    return stitched


def _project_top_or_bottom_face(face: Image.Image, camera_metadata: CameraMetadata,
                                full_width: int, full_height: int) -> Image.Image:
    input_img = Image.new("RGBA", (full_width, full_height), (0, 0, 0, 0))

    phi_length = camera_metadata.lens_projection.fov_s
    theta_length = camera_metadata.lens_projection.fov_h
    face_width = phi_length * (full_height / math.pi)
    face_height = theta_length * (full_height / math.pi)
    x = (full_width - face_width) / 2
    y = (full_height - face_height) / 2

    scaled_img = face.resize((math.ceil(face_width), math.ceil(face_height)))
    input_img.paste(scaled_img, box=(math.ceil(x), math.ceil(y)))

    input_tensor = _to_tensor(input_img).to(_device)
    reprojected_tensor = _equi2equi(input_tensor, {
        "yaw": -camera_metadata.position.yaw,
        "pitch": camera_metadata.position.pitch,
        "roll": camera_metadata.position.roll,
    })
    reprojected_tensor = reprojected_tensor.to("cpu")
    reprojected_img = _to_pil(reprojected_tensor)
    return reprojected_img


def _paste_side_face(face: Image.Image, camera_metadata: CameraMetadata,
                     full_width: int, full_height: int, stitched: Image.Image) -> None:
    phi_start = math.pi + camera_metadata.position.yaw - (camera_metadata.lens_projection.fov_s / 2)
    if phi_start < 0:
        phi_start += 2 * math.pi
    theta_start = (math.pi / 2) - (camera_metadata.lens_projection.fov_h / 2) - camera_metadata.lens_projection.cy
    phi_length = camera_metadata.lens_projection.fov_s
    theta_length = camera_metadata.lens_projection.fov_h
    face_width = phi_length * (full_height / math.pi)
    face_height = theta_length * (full_height / math.pi)
    x = phi_start * (full_height / math.pi)
    y = theta_start * (full_height / math.pi)

    scaled_img = face.resize((math.ceil(face_width), math.ceil(face_height)))
    stitched.paste(scaled_img, (math.ceil(x), math.ceil(y)))
    # front face wraps around
    if x + face.width > full_width:
        stitched.paste(scaled_img, (math.ceil(x - full_width), math.ceil(y)))
