import json
import subprocess
import sys

TIMEOUT = 10


def run_python(code: str, stdin_text: str = "") -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, "-c", code],
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=TIMEOUT,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_or_raise(code: str) -> str:
    returncode, out, err = run_python(code)
    if returncode != 0:
        lines = [line for line in err.splitlines() if line.strip()]
        raise RuntimeError(lines[-1] if lines else f"exit code {returncode}")
    return out


def echo_args(args: list[str]) -> list[str]:
    code = "import json, sys; print(json.dumps(sys.argv[1:]))"
    proc = subprocess.run(
        [sys.executable, "-c", code, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=TIMEOUT,
        check=True,
    )
    return json.loads(proc.stdout)
