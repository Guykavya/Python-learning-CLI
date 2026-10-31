import importlib.util
import tempfile
from pathlib import Path

import coverage


def measure(source, func_name, calls):
    """Return (percent, missing_lines) for running func_name(*args) for each args in calls."""
    return (0.0, [])
