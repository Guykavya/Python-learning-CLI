import sys


def install_recorder() -> list[dict]:
    """Make every breakpoint() record the caller's name and a copy of its locals."""
    records: list[dict] = []
    # TODO: define a hook and install it as sys.breakpointhook
    return records


def uninstall() -> None:
    """Put the original hook back."""
    # TODO
