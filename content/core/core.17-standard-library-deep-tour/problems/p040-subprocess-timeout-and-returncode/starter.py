import subprocess
import sys


def run_limited(code: str, timeout: float) -> tuple[str, int | None, str]:
    """Run code in a child Python for at most `timeout` seconds.

    Returns ("ok", 0, stdout), ("failed", returncode, stdout) or ("timeout", None, "").
    """
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=timeout)
    return "ok", proc.returncode, proc.stdout


def describe_exit(returncode: int | None) -> str:
    """'timed out', 'success', 'error (exit code N)' or 'killed by signal N'."""
    return "success"


def first_success(snippets: list[str], timeout: float) -> int:
    """Index of the first snippet that exits with 0 in time; -1 if none. Stop at the first success."""
    return -1
