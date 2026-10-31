# Save the code from problem.md as target.py in this folder, then run:
#     python -m pytest solution.py
from target import load_notes, save_notes


def test_round_trip(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["a"])
    assert load_notes(path) == ["a"]
