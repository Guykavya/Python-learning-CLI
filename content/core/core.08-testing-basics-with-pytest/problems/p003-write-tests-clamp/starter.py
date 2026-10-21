# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py

from target import clamp


def test_inside_the_range():
    assert clamp(5, 0, 10) == 5
