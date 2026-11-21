import inspect
import os
import subprocess
import sys

import pytest

import solution
from solution import AlreadyRunning, single_instance

ALIVE = lambda pid: True          # noqa: E731
DEAD = lambda pid: False          # noqa: E731


def test_lock_holds_our_pid_and_is_removed(tmp_path):
    lock = tmp_path / "job.lock"
    with single_instance(lock, is_alive=DEAD):
        assert lock.exists(), "Inside the with block the lock file must exist."
        assert lock.read_text(encoding="utf-8").strip() == str(os.getpid()), "Write our own pid (os.getpid()) into the lock."
    assert not lock.exists(), "After the with block the lock file must be gone."


def test_second_copy_is_refused(tmp_path):
    lock = tmp_path / "job.lock"
    with single_instance(lock, is_alive=ALIVE):
        with pytest.raises(AlreadyRunning, match=f"already running as process {os.getpid()}"):
            with single_instance(lock, is_alive=ALIVE):
                pytest.fail("the second copy must never enter its with block")
        assert lock.exists(), "The refused copy must NOT delete the running copy's lock."
        assert lock.read_text(encoding="utf-8").strip() == str(os.getpid())


def test_is_alive_gets_the_pid_as_an_int(tmp_path):
    lock = tmp_path / "job.lock"
    lock.write_text("4242\n", encoding="utf-8")
    seen = []

    def spy(pid):
        seen.append(pid)
        return True

    with pytest.raises(AlreadyRunning, match="4242"):
        with single_instance(lock, is_alive=spy):
            pass
    assert seen == [4242], f"Read the pid from the file, convert it with int(), and ask is_alive once; got {seen}"
    assert lock.read_text(encoding="utf-8") == "4242\n", "A refused copy leaves the file exactly as it was."


def test_stale_lock_is_taken_over(tmp_path):
    lock = tmp_path / "job.lock"
    lock.write_text("99999999", encoding="utf-8")
    with single_instance(lock, is_alive=DEAD):
        assert lock.read_text(encoding="utf-8").strip() == str(os.getpid()), "A dead pid means a stale lock: take it over with our pid."
    assert not lock.exists()


@pytest.mark.parametrize("content", ["", "abc", "  \n"])
def test_garbled_lock_counts_as_stale(tmp_path, content):
    lock = tmp_path / "job.lock"
    lock.write_text(content, encoding="utf-8")
    with single_instance(lock, is_alive=ALIVE):
        assert lock.read_text(encoding="utf-8").strip() == str(os.getpid()), \
            "A lock file without a valid pid cannot prove anyone is running: treat it as stale (int() raises ValueError)."


def test_lock_removed_even_after_an_exception(tmp_path):
    lock = tmp_path / "job.lock"
    with pytest.raises(ZeroDivisionError):
        with single_instance(lock, is_alive=DEAD):
            1 / 0
    assert not lock.exists(), "Put the clean-up in a finally around yield: a failing job must not leave its lock behind."


def test_lock_already_gone_is_fine(tmp_path):
    lock = tmp_path / "job.lock"
    with single_instance(lock, is_alive=DEAD):
        lock.unlink()                       # someone removed it by hand
    assert not lock.exists()


def test_uses_an_exclusive_create():
    source = inspect.getsource(solution.single_instance)
    assert "O_EXCL" in source, "Create the lock with os.open(..., O_CREAT | O_EXCL | O_WRONLY): one atomic step, not exists() then write."


CHILD = ("import sys, time, solution\n"
         "with solution.single_instance(sys.argv[1]):\n"
         "    print('ready', flush=True)\n"
         "    time.sleep(60)\n")


def test_a_real_second_process(tmp_path):
    lock = tmp_path / "job.lock"
    child = subprocess.Popen([sys.executable, "-c", CHILD, str(lock)], stdout=subprocess.PIPE, text=True)
    try:
        assert child.stdout.readline().strip() == "ready", "The child process could not take the lock."
        with pytest.raises(AlreadyRunning, match=str(child.pid)):
            with single_instance(lock):         # the default is_alive (pid_alive) sees the real child
                pass
    finally:
        child.kill()
        child.wait(timeout=30)
        child.stdout.close()
    assert lock.exists(), "A killed process leaves its lock behind (no finally runs on kill)..."
    with single_instance(lock):
        assert lock.read_text(encoding="utf-8").strip() == str(os.getpid()), "...and the next run takes over the stale lock."
