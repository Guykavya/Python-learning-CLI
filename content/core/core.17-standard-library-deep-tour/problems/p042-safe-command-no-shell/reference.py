import subprocess
import sys


def build_command(script, args):
    for arg in args:
        if not isinstance(arg, str):
            raise TypeError(f"every argument must be a str, got {arg!r}")
    return [sys.executable, str(script), *args]


def run_script(script, args, timeout=10.0):
    cmd = build_command(script, args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=timeout,
    )
    return result.stdout
