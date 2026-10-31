# Save the code from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py -p no:cacheprovider
from unittest.mock import patch

import pytest

from target import backup


@patch("target.shutil.copy")
@patch("target.os.path.exists", return_value=True)
def test_returns_bak_path(exists_mock, copy_mock):
    assert backup("/home/you/a.txt") == "/home/you/a.txt.bak"
