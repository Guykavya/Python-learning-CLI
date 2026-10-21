import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def test_example():
    assert run("09:00\n11:00\n45\n") == ["09:00-09:45", "09:45-10:30"], (
        "A third slot would end at 11:15, after closing. Only slots that end by 11:00 are allowed.")


def test_slot_ending_exactly_at_close():
    assert run("09:00\n10:00\n30\n") == ["09:00-09:30", "09:30-10:00"], (
        "A slot that ends exactly at closing time fits. Your range stop is probably one too small.")


def test_hourly_across_noon():
    assert run("11:00\n14:00\n60\n") == ["11:00-12:00", "12:00-13:00", "13:00-14:00"], "Hourly slots from 11 to 14."


def test_odd_minutes():
    assert run("08:50\n09:30\n15\n") == ["08:50-09:05", "09:05-09:20"], (
        "Work in minutes since midnight and convert back with divmod(..., 60) and :02d.")


def test_no_slot_fits():
    assert run("10:00\n10:20\n30\n") == ["No slots"], "A 30-minute slot does not fit in 20 minutes."
    assert run("10:00\n10:00\n5\n") == ["No slots"], "Start equal to end: nothing fits."


def test_invalid_length():
    assert run("10:00\n12:00\n0\n") == ["invalid length"], "A length of 0 would be an endless timetable; reject it."
