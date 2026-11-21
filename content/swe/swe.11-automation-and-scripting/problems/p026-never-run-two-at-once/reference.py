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
    is_alive = is_alive or pid_alive
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(lock_path, flags)                       # fails if the file exists
    except FileExistsError:
        try:
            pid = int(Path(lock_path).read_text(encoding="utf-8").strip())
        except ValueError:
            pid = None
        if pid is not None and is_alive(pid):
            raise AlreadyRunning(f"already running as process {pid}")
        os.unlink(lock_path)                                 # stale lock from a crashed run
        fd = os.open(lock_path, flags)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass
