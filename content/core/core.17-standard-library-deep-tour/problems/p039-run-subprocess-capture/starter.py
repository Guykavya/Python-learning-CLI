import json
import subprocess
import sys

TIMEOUT = 10


def run_python(code: str, stdin_text: str = "") -> tuple[int, str, str]:
    """Run `python -c code` with stdin_text as input. Return (returncode, stdout, stderr)."""
    return 0, "", ""


def run_or_raise(code: str) -> str:
    """Run code; return its stdout, or raise RuntimeError(last line of stderr) if it failed."""
    return ""


def echo_args(args: list[str]) -> list[str]:
    """Pass args to a child Python and return the sys.argv[1:] it received."""
    return []
