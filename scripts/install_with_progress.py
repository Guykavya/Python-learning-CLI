#!/usr/bin/env python3
"""Install the engine's packages one by one and print "N of M installed".

The ./learn and learn.cmd launchers call this on first run and after a git pull.
Standard library only, because it runs before any course package is installed.

1. pip works out every package the course needs and downloads it. pip's own
   progress bars show here; this is the large part of the wait.
2. Each package is then installed on its own, so the count is exact. The files
   are already downloaded, so this step is quick.

Usage: python install_with_progress.py <folder that holds pyproject.toml>
Exit status: 0 when everything is installed, otherwise pip's failing status.
"""

import json
import os
import subprocess
import sys
import tempfile

ENGINE = "learn-engine"  # the name in pyproject.toml; installed last, from the folder itself


def _norm(name):
    """Package names compare case-insensitively, with '_' and '.' the same as '-'."""
    return name.lower().replace("_", "-").replace(".", "-")


def _pip(*args, capture=False):
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", *args],
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _failed(result, what):
    print(f"Could not install {what}:", file=sys.stderr)
    print((result.stdout or "") + (result.stderr or ""), file=sys.stderr)
    return result.returncode or 1


def main(argv):
    if len(argv) != 2:
        print("Usage: install_with_progress.py <folder that holds pyproject.toml>", file=sys.stderr)
        return 2
    project = os.path.abspath(argv[1])

    print("Checking which packages the engine needs and downloading them.", flush=True)
    print("pip's progress bars are below; this is the large part of the wait.", flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        report = os.path.join(tmp, "report.json")
        # A dry run: pip resolves everything, downloads it into its cache, and writes what it would install.
        result = _pip("--dry-run", "--progress-bar", "on", "--report", report, "-e", project)
        if result.returncode != 0:
            return result.returncode
        with open(report, encoding="utf-8") as f:
            wanted = json.load(f)["install"]

    pins = []
    for item in wanted:
        meta = item["metadata"]
        if _norm(meta["name"]) != ENGINE:
            pins.append(f"{meta['name']}=={meta['version']}")

    total = len(pins) + 1  # the packages, then the engine itself
    print(f"Found {total} packages to install. Installing them one at a time:", flush=True)
    for done, pin in enumerate(pins, 1):
        # The files are cached by now, so pip only unpacks and copies them. Output is captured
        # so the count lines stay readable; a failure prints pip's full message below.
        result = _pip("--no-deps", "--progress-bar", "off", pin, capture=True)
        if result.returncode != 0:
            return _failed(result, pin)
        print(f"  {done} of {total} installed: {pin.replace('==', ' ')}", flush=True)

    result = _pip("--no-deps", "--progress-bar", "off", "-e", project, capture=True)
    if result.returncode != 0:
        return _failed(result, "the engine")
    print(f"  {total} of {total} installed: the engine ({ENGINE})", flush=True)
    print("All packages are installed.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
