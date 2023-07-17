def is_third_party_panoid(panoid: str) -> bool:
    """
    Returns whether a pano ID points to a third-party panorama rather than an official Google panorama.

    :param panoid: The pano ID.
    :return: Whether the pano ID points to a third-party panorama.
    """
    return len(panoid) > 22
