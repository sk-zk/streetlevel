import math
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Tuple, Optional, Union

import pyexiv2
from PIL import Image


def save_with_metadata(image: Image.Image, path: str, pil_args: dict,
                       panoid: str, lat: float, lon: float, altitude: Optional[float], date: Union[datetime, str],
                       heading: float, pitch: Optional[float], roll: Optional[float], creator: str) -> None:
    suffix = Path(path).suffix.lower()
    # only write exif/xmp to JPG files
    if not (suffix == ".jpg" or suffix == ".jpeg"):
        image.save(path, **pil_args)
        return

    buffer = BytesIO()
    image.save(buffer, format="jpeg", **pil_args)
    buffer.seek(0)
    with pyexiv2.ImageData(buffer.read()) as ximg:
        exif = {
            "Exif.Image.DateTime": date.strftime("%Y:%m:%d %H:%M:%S") if isinstance(date, datetime) else date,
            "Exif.Image.ImageID": panoid,
            "Exif.Image.Artist": creator,
            "Exif.Image.Copyright": creator,
            "Exif.GPSInfo.GPSVersionID": 2,
            "Exif.GPSInfo.GPSLatitude": decimal_to_exif(lat),
            "Exif.GPSInfo.GPSLatitudeRef": "N" if lat >= 0 else "S",
            "Exif.GPSInfo.GPSLongitude": decimal_to_exif(lon),
            "Exif.GPSInfo.GPSLongitudeRef": "E" if lon >= 0 else "W",
        }
        if altitude:
            exif["Exif.GPSInfo.GPSAltitude"] = altitude_to_exif(altitude)
            exif["Exif.GPSInfo.GPSAltitudeRef"] = 0 if altitude >= 0 else 1
        ximg.modify_exif(exif)
        xmp = {
            "Xmp.GPano.UsePanoramaViewer": True,
            "Xmp.GPano.ProjectionType": "equirectangular",
            "Xmp.GPano.PoseHeadingDegrees": math.degrees(heading),
            "Xmp.GPano.CroppedAreaImageWidthPixels": image.width,
            "Xmp.GPano.CroppedAreaImageHeightPixels": image.height,
            "Xmp.GPano.FullPanoWidthPixels": image.width,
            "Xmp.GPano.FullPanoHeightPixels": image.height,
            "Xmp.GPano.CroppedAreaLeftPixels": 0,
            "Xmp.GPano.CroppedAreaTopPixels": 0,
        }
        if pitch:
            xmp["Xmp.GPano.PosePitchDegrees"] = math.degrees(pitch)
        if roll:
            xmp["Xmp.GPano.PoseRollDegrees"] = math.degrees(roll)
        ximg.modify_xmp(xmp)
        with open(path, "wb") as f:
            f.write(ximg.get_bytes())


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
