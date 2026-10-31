# Save the code from problem.md as wordstat.py in this folder to try your tests:
#     python -m pytest solution.py
import wordstat


def test_missing_file(tmp_path):
    assert wordstat.main([str(tmp_path / "nope.txt")]) == 2
