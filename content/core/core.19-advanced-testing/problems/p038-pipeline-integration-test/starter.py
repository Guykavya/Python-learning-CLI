# Save the code from problem.md as pipeline.py in this folder to try your tests:
#     python -m pytest solution.py
from pipeline import run


def test_simple_file(tmp_path):
    src = tmp_path / "in.csv"
    src.write_text("date,category,amount\n2025-01-01,food,10\n")
    dst = tmp_path / "out.csv"
    assert run(src, dst) == 1
