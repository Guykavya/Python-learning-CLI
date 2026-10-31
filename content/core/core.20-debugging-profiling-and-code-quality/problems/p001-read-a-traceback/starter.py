import re


def blame(tb_text: str) -> tuple[str, int, str]:
    """(file, line, function) of the innermost frame of the last traceback."""
    return ("", 0, "")
