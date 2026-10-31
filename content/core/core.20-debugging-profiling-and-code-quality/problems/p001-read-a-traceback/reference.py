import re

FRAME_RE = re.compile(r'^  File "(.+?)", line (\d+)(?:, in (.+))?$', re.MULTILINE)


def blame(tb_text: str) -> tuple[str, int, str]:
    """(file, line, function) of the innermost frame of the last traceback."""
    frames = FRAME_RE.findall(tb_text)
    if not frames:
        raise ValueError("no frame lines in this text")
    file, line, function = frames[-1]
    return file, int(line), function
