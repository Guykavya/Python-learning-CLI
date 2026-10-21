"""Check your work: run pytest for code problems, compare answers for trace problems."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from learn.content import Problem

TIMEOUT_SECONDS = 60
COPY_SUFFIXES = {".py", ".txt", ".csv", ".json", ".md", ".toml", ".yaml", ".yml"}


@dataclass
class CheckResult:
    passed: bool
    tests_passed: int
    tests_total: int
    output: str
    self_rating: int | None = None

    @property
    def not_ready(self) -> bool:
        """Nothing to check yet (empty answer). Not counted as an attempt."""
        return not self.passed and self.tests_total == 0


def run_code_tests(problem: Problem, solution_dir: Path, solution_file: Path | None = None) -> CheckResult:
    """Copy your files and the problem's tests into a temp folder and run pytest there.

    Nothing is written into the content folder or your work folder.
    """
    test_file = problem.file("test_solution.py")
    if not test_file.exists():
        return CheckResult(False, 0, 0, f"This problem has no test_solution.py ({problem.path})")

    with tempfile.TemporaryDirectory(prefix="learn-check-") as tmp:
        tmpd = Path(tmp)
        if solution_file is not None:
            shutil.copy(solution_file, tmpd / "solution.py")
        else:
            for f in solution_dir.iterdir():
                if f.is_file() and f.suffix in COPY_SUFFIXES:
                    shutil.copy(f, tmpd / f.name)
        shutil.copy(test_file, tmpd / "test_solution.py")
        for extra in ("conftest.py",):
            if problem.file(extra).exists():
                shutil.copy(problem.file(extra), tmpd / extra)
        fixtures = problem.file("fixtures")
        if fixtures.is_dir():
            shutil.copytree(fixtures, tmpd / "fixtures")

        report = tmpd / "_report.xml"
        cmd = [
            sys.executable, "-m", "pytest", "test_solution.py",
            "-q", "--no-header", "-p", "no:cacheprovider", "--tb=short",
            f"--junitxml={report}",
        ]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(tmpd))
        try:
            proc = subprocess.run(cmd, cwd=tmpd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, env=env)
        except subprocess.TimeoutExpired:
            return CheckResult(
                False, 0, 0,
                f"Stopped after {TIMEOUT_SECONDS} seconds. Look for an infinite loop, "
                "or input() waiting for typing inside a function the tests call.",
            )
        output = (proc.stdout + proc.stderr).replace(str(tmpd), str(solution_dir))
        total, failed = _parse_junit(report)

    if total == 0:
        return CheckResult(False, 0, 0, output or "No tests ran.")
    return CheckResult(failed == 0 and proc.returncode == 0, total - failed, total, output)


def _parse_junit(report: Path) -> tuple[int, int]:
    if not report.exists():
        return 0, 0
    root = ET.parse(report).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    total = failed = 0
    for s in suites:
        t = int(s.get("tests", 0))
        skipped = int(s.get("skipped", 0))
        total += t - skipped
        failed += int(s.get("failures", 0)) + int(s.get("errors", 0))
    return total, failed


def normalise(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return [line for line in lines if not line.lstrip().startswith("#")] if lines else []


def check_trace(problem: Problem, answer_file: Path) -> CheckResult:
    expected = normalise(problem.read("expected.txt"))
    given = normalise(answer_file.read_text()) if answer_file.exists() else []
    if not given:
        return CheckResult(False, 0, 0, f"Write your predicted output in {answer_file} first.")
    if given == expected:
        return CheckResult(True, 1, 1, "Your prediction matches the real output exactly.")
    import difflib

    diff = "\n".join(
        difflib.unified_diff(expected, given, fromfile="real output", tofile="your prediction", lineterm="")
    )
    return CheckResult(False, 0, 1, "Your prediction differs from the real output:\n" + diff)


def explain_word_count(answer_file: Path) -> int:
    if not answer_file.exists():
        return 0
    text = "\n".join(normalise(answer_file.read_text()))
    return len(text.split())
