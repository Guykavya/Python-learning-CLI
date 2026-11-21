import os
from contextlib import contextmanager
from pathlib import Path


class AlreadyRunning(Exception):
    pass


def pid_alive(pid):
    """True if a process with this id exists. Given; works on Linux, macOS and Windows."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            ok = kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return bool(ok) and code.value == 259                  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)                                            # signal 0: "does it exist?", nothing is sent
    except ProcessLookupError:
        return False
    except PermissionError:
        return True                                                # it exists, but belongs to another user
    return True


@contextmanager
def single_instance(lock_path, is_alive=None):
    """Hold an exclusive lock file containing our pid; AlreadyRunning if a live process holds it."""
    # TODO: O_CREAT | O_EXCL, stale-lock take-over, always remove on exit
    yield
