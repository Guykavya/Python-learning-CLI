import subprocess


class ToolFailed(Exception):
    """A tool failed. Attributes: command (list), code (int or None), stderr_tail (last <= 5 stderr lines)."""

    def __init__(self, command, code, stderr_tail, message):
        self.command, self.code, self.stderr_tail = command, code, stderr_tail
        if stderr_tail:
            message = message + "\n" + "\n".join(stderr_tail)
        super().__init__(message)


def _tail(text, n=5):
    if text is None:
        return []
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return text.splitlines()[-n:]


def run_tool(args, timeout):
    """Run args; return stdout. Any failure becomes ToolFailed."""
    command = " ".join(str(a) for a in args)
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True, timeout=timeout).stdout
    except subprocess.CalledProcessError as e:
        raise ToolFailed(args, e.returncode, _tail(e.stderr), f"{command} failed with exit code {e.returncode}") from e
    except subprocess.TimeoutExpired as e:
        raise ToolFailed(args, None, _tail(e.stderr), f"{command} timed out after {timeout}s") from e
    except FileNotFoundError as e:
        raise ToolFailed(args, None, [], f"{command} could not start: {e}") from e
