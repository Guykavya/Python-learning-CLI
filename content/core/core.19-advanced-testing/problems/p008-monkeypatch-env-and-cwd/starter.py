# Save the code from problem.md as target.py in this folder, then run:
#     python -m pytest solution.py
from target import load_config


def test_defaults():
    assert load_config()["name"] == "app"
