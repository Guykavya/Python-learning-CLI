import ast
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is copied to a temporary folder and real pytest runs
# on it twice, writing a JUnit report that says for each test passed / failed / skipped / xfailed.
# The checker also looks at your decorators (reasons, strict, skipif condition).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()
TREE = ast.parse(LEARNER_SOURCE)
FUNCS = {n.name: n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef)}
ORIGINAL_BODIES = {
    "test_slugify_basic": 'assert slugify("Hello World") == "hello-world"',
    "test_slugify_accents": 'assert slugify("Cr\\u00e8me Br\\u00fbl\\u00e9e") == "creme-brulee"',
    "test_needs_python_4": "assert sys.version_info >= (4, 0)",
    "test_not_written_yet": "raise NotImplementedError",
    "test_sum_of_a_million": "assert sum(range(1_000_000)) == 499999500000",
}


def run(extra=()):
    with tempfile.TemporaryDirectory(prefix="learn-mark-") as tmp:
        tmp = Path(tmp)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header", "-p", "no:cacheprovider",
                 "--tb=short", "--junitxml=report.xml", *extra],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return {}, "pytest timed out"
        results = {}
        report = tmp / "report.xml"
        if report.exists():
            for tc in ET.parse(report).getroot().iter("testcase"):
                status = "passed"
                for child in tc:
                    if child.tag in ("failure", "error"):
                        status = "failed"
                        break
                    if child.tag == "skipped":
                        status = "xfailed" if child.get("type") == "pytest.xfail" else "skipped"
                results[tc.get("name")] = status
    return results, (proc.stdout + proc.stderr).replace(str(tmp), ".")


@lru_cache(maxsize=None)
def default_run():
    return run()


def decorators(name):
    """Return {marker name: ast.Call or ast.Attribute} for the pytest.mark.<x> decorators of a test."""
    found = {}
    for dec in FUNCS[name].decorator_list:
        node = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute) and node.value.attr == "mark":
            found[node.attr] = dec
    return found


def test_the_test_functions_were_not_changed():
    for name, body in ORIGINAL_BODIES.items():
        assert name in FUNCS, f"{name} is missing. Keep all five tests; only add markers."
        got = ast.dump(ast.parse(body).body[0])
        mine = [ast.dump(s) for s in FUNCS[name].body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        assert got in mine and len(mine) == 1, (
            f"The body of {name} was changed. Markers decide what happens to a test; "
            "do not edit the test to make it pass.")


def test_default_run_has_no_failures():
    results, out = default_run()
    failed = sorted(n for n, s in results.items() if s == "failed")
    assert not failed, ("These tests still FAIL or ERROR: " + ", ".join(failed) +
                        ". Mark known bugs with xfail, not-yet-possible tests with skip/skipif. pytest said:\n" + out[-800:])


def test_known_bug_is_xfail():
    results, _ = default_run()
    assert results.get("test_slugify_accents") == "xfailed", (
        "test_slugify_accents fails because of a known bug: use @pytest.mark.xfail(reason=..., strict=True) "
        f"so it is reported as xfailed (got {results.get('test_slugify_accents')!r}).")
    call = decorators("test_slugify_accents").get("xfail")
    assert isinstance(call, ast.Call) and any(k.arg == "strict" and getattr(k.value, "value", None) is True for k in call.keywords), (
        "Add strict=True to the xfail: when someone fixes slugify, the XPASS then turns into a failure "
        "that reminds you to remove the marker.")


def test_condition_based_skip_uses_skipif():
    results, _ = default_run()
    assert results.get("test_needs_python_4") == "skipped", "test_needs_python_4 should be skipped on Python 3."
    call = decorators("test_needs_python_4").get("skipif")
    assert isinstance(call, ast.Call) and call.args, (
        "This test is only impossible when sys.version_info < (4, 0): use "
        "@pytest.mark.skipif(<condition>, reason=...), not an unconditional skip. On Python 4 it should run.")


def test_unfinished_test_is_skipped():
    results, _ = default_run()
    assert results.get("test_not_written_yet") == "skipped", (
        "test_not_written_yet is a placeholder: @pytest.mark.skip(reason=...) it.")
    assert "skip" in decorators("test_not_written_yet"), "Use @pytest.mark.skip for an unconditional skip."


def test_every_skip_and_xfail_has_a_reason():
    for name in FUNCS:
        for marker in ("skip", "skipif", "xfail"):
            dec = decorators(name).get(marker) if name.startswith("test_") else None
            if dec is None:
                continue
            assert isinstance(dec, ast.Call) and any(k.arg == "reason" for k in dec.keywords), (
                f"{name}: give @pytest.mark.{marker} a reason=... so the report says WHY.")


def test_the_two_healthy_tests_still_pass():
    results, _ = default_run()
    assert results.get("test_slugify_basic") == "passed", "test_slugify_basic needs no marker."
    assert results.get("test_sum_of_a_million") == "passed", "test_sum_of_a_million should still run by default."


def test_slow_marker_lets_you_deselect_the_slow_test():
    assert "slow" in decorators("test_sum_of_a_million"), (
        "Mark test_sum_of_a_million with the custom marker @pytest.mark.slow.")
    results, out = run(("-m", "not slow"))
    assert "test_sum_of_a_million" not in results, (
        "pytest -m 'not slow' must deselect test_sum_of_a_million. Is the marker spelled exactly 'slow'?")
    assert results.get("test_slugify_basic") == "passed", "Other tests must still run under -m 'not slow'. " + out[-300:]
