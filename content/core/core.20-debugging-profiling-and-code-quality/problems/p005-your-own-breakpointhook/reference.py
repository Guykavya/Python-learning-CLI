import sys


def install_recorder() -> list[dict]:
    """Make every breakpoint() record the caller's name and a copy of its locals."""
    records: list[dict] = []

    def hook(*args, **kwargs):
        frame = sys._getframe(1)  # the code that called breakpoint()
        records.append({"function": frame.f_code.co_name, "locals": dict(frame.f_locals)})

    sys.breakpointhook = hook
    return records


def uninstall() -> None:
    """Put the original hook back."""
    sys.breakpointhook = sys.__breakpointhook__
