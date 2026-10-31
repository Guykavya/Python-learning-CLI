import subprocess
import sys


def build_command(script, args):
    """Return [sys.executable, str(script), *args]; TypeError for a non-str argument."""
    return []


def run_script(script, args, timeout=10.0):
    """Run the command without a shell (check=True, timeout) and return its stdout text."""
    return ""
