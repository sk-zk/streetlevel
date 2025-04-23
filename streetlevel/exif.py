import math
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Tuple, Optional, Union

import pyexiv2
from PIL import Image


@dataclass
class OutputMetadata:
    panoid: str
    lat: float
    lon: float
    creator: str
    is_equirectangular: bool
    altitude: Optional[float] = None
    date: Union[datetime, str, None] = None
    heading: Optional[float] = None
    pitch: Optional[float] = None
    roll: Optional[float] = None


def save_with_metadata(image: Image.Image, path: str, pil_args: dict,
                       metadata: OutputMetadata) -> None:
    suffix = Path(path).suffix.lower()
    # only write exif/xmp to JPG files
    if not (suffix == ".jpg" or suffix == ".jpeg"):
        image.save(path, **pil_args)
        return

    buffer = BytesIO()
    image.save(buffer, format="jpeg", **pil_args)
    buffer.seek(0)

    m = metadata
    with pyexiv2.ImageData(buffer.read()) as ximg:
        exif = _build_exif_object(m)
        ximg.modify_exif(exif)

        if m.is_equirectangular:
            xmp = _build_xmp_object(image, m)
            ximg.modify_xmp(xmp)

        with open(path, "wb") as f:
            f.write(ximg.get_bytes())


def _build_xmp_object(image, m: OutputMetadata):
    xmp = {
        "Xmp.GPano.UsePanoramaViewer": True,
        "Xmp.GPano.ProjectionType": "equirectangular",
        "Xmp.GPano.CroppedAreaImageWidthPixels": image.width,
        "Xmp.GPano.CroppedAreaImageHeightPixels": image.height,
        "Xmp.GPano.FullPanoWidthPixels": image.width,
        "Xmp.GPano.FullPanoHeightPixels": image.height,
        "Xmp.GPano.CroppedAreaLeftPixels": 0,
        "Xmp.GPano.CroppedAreaTopPixels": 0,
    }
    if m.heading:
        xmp["Xmp.GPano.PoseHeadingDegrees"] = math.degrees(m.heading) % 360
    if m.pitch:
        xmp["Xmp.GPano.PosePitchDegrees"] = math.degrees(m.pitch)
    if m.roll:
        xmp["Xmp.GPano.PoseRollDegrees"] = math.degrees(m.roll)
    return xmp


def _build_exif_object(m: OutputMetadata) -> dict:
    exif = {
        "Exif.Image.DateTime": m.date.strftime("%Y:%m:%d %H:%M:%S") if isinstance(m.date, datetime) else m.date,
        "Exif.Image.ImageID": m.panoid,
        "Exif.Image.Artist": m.creator,
        "Exif.Image.Copyright": m.creator,
        "Exif.GPSInfo.GPSVersionID": 2,
        "Exif.GPSInfo.GPSLatitude": decimal_to_exif(m.lat),
        "Exif.GPSInfo.GPSLatitudeRef": "N" if m.lat >= 0 else "S",
        "Exif.GPSInfo.GPSLongitude": decimal_to_exif(m.lon),
        "Exif.GPSInfo.GPSLongitudeRef": "E" if m.lon >= 0 else "W",
    }
    if m.altitude:
        exif["Exif.GPSInfo.GPSAltitude"] = altitude_to_exif(m.altitude)
        exif["Exif.GPSInfo.GPSAltitudeRef"] = 0 if m.altitude >= 0 else 1
    return exif


def decimal_to_dms(coord: float) -> Tuple[int, int, float]:
    """
    Converts a decimal geographic coordinate to degrees/minutes/seconds.

    :param coord: The decimal coordinate.
    :return: The DMS equivalent.
    """
    degs = int(coord)
    mins_float = (coord - degs) * 60
    mins = int(mins_float)
    secs_float = (mins_float - mins) * 60
    return degs, mins, secs_float


def decimal_to_exif(coord: float) -> str:
    """
    Converts a decimal geographic coordinate to a degrees/minutes/seconds string
    in the format expected by the Exif library pyexiv2.

    :param coord: The decimal coordinate.
    :return: A string representation of the DMS coordinate.
    """
    degs, mins, secs_float = decimal_to_dms(abs(coord))
    return f"{degs}/1 {mins}/1 {int(secs_float * 100)}/100"


def altitude_to_exif(alt: float) -> str:
    """
    Converts an altitude to a string
    in the format expected by the Exif library pyexiv2.

    :param alt: The altitude in meters.
    :return: A string representation of the altitude.
    """
    return f"{int(abs(alt) * 100)}/100"
