import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LogEntry:
    timestamp: str
    level: str
    module: str
    message: str


def parse_line(line: str) -> LogEntry | None:
    return None


def summarise(path) -> dict:
    return {}
