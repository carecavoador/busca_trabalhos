"""OS Number and OS related methods."""
import re
from dataclasses import dataclass


@dataclass
class OSNumber:
    """OSNumber object."""

    number: int
    version: int


def guess_os_number(filename: str) -> tuple[int, int]:
    """Tries to guess the OS Number and Version from a given string."""

    os_pattern = r"(\d{4,}).*[vV](\d+)"  # regex to match OS Number and Version
    _os_number = re.search(os_pattern, filename)
    if _os_number:
        os_number = _os_number.group(1)
        os_version = _os_number.group(2)
        return (os_number, os_version)
    else:
        return None
