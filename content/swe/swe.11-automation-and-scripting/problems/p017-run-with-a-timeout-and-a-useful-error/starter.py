import subprocess


class ToolFailed(Exception):
    """A tool failed. Attributes: command (list), code (int or None), stderr_tail (last <= 5 stderr lines)."""

    def __init__(self, command, code, stderr_tail, message):
        # TODO: keep the attributes; add the tail lines to the message
        super().__init__(message)


def run_tool(args, timeout):
    """Run args; return stdout. Any failure becomes ToolFailed."""
    # TODO: capture_output, text, check, timeout; three kinds of failure
    return subprocess.run(args, capture_output=True, text=True).stdout
