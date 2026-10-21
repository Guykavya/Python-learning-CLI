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
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


EXAMPLE_IN = """add ravi 98111
add Asha 98200
add meena 98111
add asha 90000
find a
update ravi 98200
update ravi 97000
phone 97000
phone 98111
delete kiran
list
count
help
quit
"""

EXAMPLE_OUT = [
    "Added ravi", "Added Asha", "98111 is already used by ravi", "Added asha",
    "Asha: 98200", "asha: 90000", "98200 is already used by Asha", "Updated ravi",
    "97000 belongs to ravi", "Unknown number 98111", "No contact named kiran",
    "Asha: 98200", "asha: 90000", "ravi: 97000", "Contacts: 3", "Unknown command", "Goodbye"]


def test_example():
    assert run(EXAMPLE_IN) == EXAMPLE_OUT


def test_empty_book():
    assert run("list\ncount\nfind x\nphone 1\nquit\n") == [
        "Contact book is empty", "Contacts: 0", "No matches", "Unknown number 1", "Goodbye"]


def test_duplicate_name():
    assert run("add a 1\nadd a 2\nphone 2\nquit\n") == [
        "Added a", "a already exists", "Unknown number 2", "Goodbye"], (
        "A rejected add must not store anything, in either dict.")


def test_delete_frees_phone():
    out = run("add a 1\ndelete a\nphone 1\nadd b 1\nquit\n")
    assert out == ["Added a", "Deleted a", "Unknown number 1", "Added b", "Goodbye"], (
        "After delete, the phone number must be free again. Remove it from the phone dict too.")


def test_update_frees_old_phone():
    out = run("add a 1\nupdate a 2\nphone 1\nphone 2\nadd b 1\nquit\n")
    assert out == ["Added a", "Updated a", "Unknown number 1", "2 belongs to a", "Added b", "Goodbye"], (
        "update must remove the OLD phone from the reverse dict and add the new one.")


def test_update_to_own_number():
    assert run("add a 1\nupdate a 1\nquit\n") == ["Added a", "Updated a", "Goodbye"], (
        "Setting a contact's phone to the number it already has is not a conflict.")


def test_update_unknown():
    assert run("update zed 5\nquit\n") == ["No contact named zed", "Goodbye"]


def test_sorting_ignores_case():
    out = run("add bob 1\nadd Carl 2\nadd alice 3\nlist\nquit\n")
    assert out[3:6] == ["alice: 3", "bob: 1", "Carl: 2"], (
        "Sort with key=str.lower. Plain sorting puts 'Carl' before 'alice'.")


def test_find_prefix_ignores_case():
    out = run("add Ravi 1\nadd rajesh 2\nadd meena 3\nfind RA\nquit\n")
    assert out[3:5] == ["rajesh: 2", "Ravi: 1"], "find matches the prefix ignoring case, sorted ignoring case."


def test_wrong_number_of_words_is_unknown():
    assert run("add onlyname\ndelete\nquit\n") == ["Unknown command", "Unknown command", "Goodbye"], (
        "A command with the wrong number of words is an unknown command.")


def test_many_phone_lookups_fast():
    n = 30000
    lines = [f"add p{i} {100000 + i}" for i in range(n)]
    lines += [f"phone {100000 + i}" for i in range(n)]
    lines.append("quit")
    out = run("\n".join(lines) + "\n")
    assert out[-2] == f"{100000 + n - 1} belongs to p{n - 1}", (
        "Reverse lookups must be O(1). Searching all contacts for each phone is O(n) per lookup; "
        "keep a second dict from phone to name.")
