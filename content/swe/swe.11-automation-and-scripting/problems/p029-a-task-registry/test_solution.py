import json
import subprocess
import sys

import pytest

import solution
from solution import TASKS, main, task


@pytest.fixture(autouse=True)
def keep_registry():
    saved = dict(TASKS)
    yield
    TASKS.clear()
    TASKS.update(saved)


def status(folder, name):
    return json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))


def test_decorator_registers_and_returns_the_function():
    def tmp(args):
        return 42

    result = task("tmp")(tmp)
    assert result is tmp, "The decorator must return the function unchanged (otherwise the name becomes None)."
    assert TASKS["tmp"] is tmp, "Store the function in TASKS under its name."


def test_example_tasks_are_registered():
    assert {"hello", "echo"} <= set(TASKS), "The starter's @task('hello') and @task('echo') must end up in TASKS."
    assert solution.hello([]) == "said hello", "A decorated task is still callable as a plain function."


def test_duplicate_name_is_refused():
    with pytest.raises(ValueError):
        @task("hello")
        def other(args):
            pass
    assert TASKS["hello"] is solution.hello, "The first registration must stay."


def test_list(capsys):
    assert main(["list"]) == 0
    assert capsys.readouterr().out.splitlines() == ["echo", "hello"], "list prints the task names, sorted, one per line."


def test_run_writes_status(tmp_path, capsys):
    assert main(["--status-dir", str(tmp_path), "run", "hello"]) == 0
    assert "hello from a registered task" in capsys.readouterr().out
    s = status(tmp_path, "hello")
    assert s["ok"] is True and s["result"] == "said hello", "Run the task through run_job so a status file records it."


def test_extra_args_reach_the_task_untouched(tmp_path, capsys):
    assert main(["--status-dir", str(tmp_path), "run", "echo", "a", "-x", "b"]) == 0, \
        "Words after the task name, even '-x', belong to the task: nargs=argparse.REMAINDER."
    assert capsys.readouterr().out.strip() == "a -x b"
    assert status(tmp_path, "echo")["result"] == 3


def test_new_task_is_available_at_once(tmp_path, capsys):
    @task("count")
    def count(args):
        print(len(args))

    assert main(["--status-dir", str(tmp_path), "run", "count", "1", "2"]) == 0
    assert capsys.readouterr().out.strip() == "2"
    main(["list"])
    assert "count" in capsys.readouterr().out.split(), "A task registered later appears in list too."


def test_failing_task_is_exit_1_with_failed_status(tmp_path):
    @task("broken")
    def broken(args):
        raise RuntimeError("disk not mounted")

    assert main(["--status-dir", str(tmp_path), "run", "broken"]) == 1, "A task that raises gives exit code 1 (run_job's code)."
    s = status(tmp_path, "broken")
    assert s["ok"] is False and "disk not mounted" in s["error"]


def test_unknown_task_is_exit_2_with_the_list(tmp_path, capsys):
    assert main(["--status-dir", str(tmp_path), "run", "backup"]) == 2, "An unknown task is a usage error: return 2."
    out, err = capsys.readouterr()
    assert "unknown task 'backup'" in err and "known tasks: echo, hello" in err, f"Name the task and list the known ones on stderr; got {err!r}"
    assert out == "" and not (tmp_path / "backup.json").exists(), "Nothing runs, nothing is recorded."


def test_as_a_real_program(tmp_path):
    r = subprocess.run([sys.executable, solution.__file__, "--status-dir", str(tmp_path), "run", "hello"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "hello from a registered task" in r.stdout, f"stderr: {r.stderr}"
    assert (tmp_path / "hello.json").exists()
    r = subprocess.run([sys.executable, solution.__file__, "run", "nope"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 2, "Keep sys.exit(main()) so 2 reaches the shell."
