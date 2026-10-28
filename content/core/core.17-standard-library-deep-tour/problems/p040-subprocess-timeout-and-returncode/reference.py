import subprocess
import sys


def run_limited(code: str, timeout: float) -> tuple[str, int | None, str]:
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "timeout", None, ""
    status = "ok" if proc.returncode == 0 else "failed"
    return status, proc.returncode, proc.stdout


def describe_exit(returncode: int | None) -> str:
    if returncode is None:
        return "timed out"
    if returncode == 0:
        return "success"
    if returncode > 0:
        return f"error (exit code {returncode})"
    return f"killed by signal {-returncode}"


def first_success(snippets: list[str], timeout: float) -> int:
    for index, code in enumerate(snippets):
        status, _, _ = run_limited(code, timeout)
        if status == "ok":
            return index
    return -1
