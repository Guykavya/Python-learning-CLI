## Approach

`patch("target.shutil.copy")` replaces the name `copy` inside the module `shutil` for the duration of
the test and puts it back afterwards, even when the test fails. As a decorator it passes the mock as an
extra argument (bottom decorator first); as a context manager it gives the mock after `as`. Each bug
changes the copy call (arguments, count, order relative to the check) or the result, so the tests
assert the whole call with `assert_called_once_with` and the **absence** of a call with `assert_not_called`.

## Code

```python
from unittest.mock import patch

import pytest

from target import backup

P = "/home/you/notes.txt"


@patch("target.shutil.copy")
@patch("target.os.path.exists", return_value=True)
def test_copies_to_bak_and_returns_the_new_path(exists_mock, copy_mock):
    assert backup(P) == P + ".bak", "backup must return the path of the copy."
    copy_mock.assert_called_once_with(P, P + ".bak")


def test_missing_file_raises_and_copies_nothing():
    with patch("target.os.path.exists", return_value=False):
        with patch("target.shutil.copy") as copy_mock:
            with pytest.raises(FileNotFoundError):
                backup(P)
            copy_mock.assert_not_called()


@patch("target.shutil.copy")
@patch("target.os.path.exists", return_value=True)
def test_exists_is_asked_about_the_original(exists_mock, copy_mock):
    backup(P)
    exists_mock.assert_called_once_with(P)


def test_copy_failure_is_not_hidden():
    with patch("target.os.path.exists", return_value=True):
        with patch("target.shutil.copy", side_effect=PermissionError("no")):
            with pytest.raises(PermissionError):
                backup(P)
```

## Complexity

Not applicable.

## Another way

`monkeypatch.setattr` (chapter section 6) does the same job as `patch` without the stacking of mock
arguments, but it does not record calls, so you would write your own spy.
