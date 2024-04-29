import math
from datetime import datetime
from typing import Optional, List

from streetlevel.streetside.panorama import StreetsidePanorama


def parse_panoramas_id_response(response: dict) -> Optional[StreetsidePanorama]:
    if len(response) < 2:
        return None
    return parse_panorama(response[1])


def parse_panoramas(response: dict) -> List[StreetsidePanorama]:
    panos = []
    for pano in response[1:]:  # first object is elapsed time
        pano_obj = parse_panorama(pano)
        panos.append(pano_obj)
    return panos


def parse_panorama(pano: dict) -> StreetsidePanorama:
    # TODO: parse bl, nbn, pbn, ad fields
    # as it turns out, months/days without leading zeros
    # don't have a cross-platform format code in strptime.
    # wanna guess what kind of dates bing returns?
    datestr = pano["cd"]
    datestr = datestr.split("/")
    datestr[0] = datestr[0].rjust(2, "0")
    datestr[1] = datestr[1].rjust(2, "0")
    datestr = "/".join(datestr)
    date = datetime.strptime(datestr, "%m/%d/%Y %I:%M:%S %p")
    pano_obj = StreetsidePanorama(
        id=pano["id"],
        lat=pano["la"],
        lon=pano["lo"],
        date=date,
        next=pano["ne"] if "ne" in pano else None,
        previous=pano["pr"] if "pr" in pano else None,
        elevation=pano["al"] if "al" in pano else None,
        heading=math.radians(pano["he"]) if "he" in pano else None,
        pitch=math.radians(pano["pi"]) if "pi" in pano else None,
        roll=math.radians(pano["ro"]) if "ro" in pano else None,
        max_zoom=int(pano["ml"])
    )
    return pano_obj
