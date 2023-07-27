import numpy as np


def to_base4(n: int) -> str:
    """
    Converts an integer to a base 4 string.

    :param n: The integer.
    :return: The base 4 representation of the integer.
    """
    return np.base_repr(n, 4)


def from_base4(n: str) -> int:
    """
    Converts a string containing a base 4 number to integer.

    :param n: The string containing a base 4 number.
    :return: The integer represented by the string.
    """
    return int(n, 4)
