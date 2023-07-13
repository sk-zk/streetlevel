def is_third_party_panoid(panoid: str) -> bool:
    """
    Returns whether a panoid refers to a third-party panorama.
    """
    return len(panoid) > 22