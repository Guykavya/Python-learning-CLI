# patch as decorator and context manager

`backup` copies a file and uses two things you must not run for real in a unit test: `os.path.exists`
and `shutil.copy`. `unittest.mock.patch` swaps a name for a mock for a short time. It comes in two
forms:

```python
@patch("target.shutil.copy")             # decorator: the mock is passed as an argument
def test_a(copy_mock): ...

def test_b():
    with patch("target.shutil.copy") as copy_mock:   # context manager: active inside the block
        ...
```

The code under test:

```python
import os
import shutil


def backup(path):
    """Copy the file to path + '.bak' and return the new path. Missing file: FileNotFoundError."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    destination = path + ".bak"
    shutil.copy(path, destination)
    return destination
```

Write tests (`from target import backup`, `from unittest.mock import patch`) so that **no real file
is touched** (use a made-up path such as `/home/you/notes.txt`) and that:

- use `patch` as a **decorator** in at least one test and as a **context manager** in at least one;
- check the returned path, the exact `shutil.copy` call, and that the copy is **not** called for a missing file;
- check that a missing file raises `FileNotFoundError`.

Write at least 4 test functions. Six buggy versions are tried.

**Example**

```python
@patch("target.shutil.copy")
@patch("target.os.path.exists", return_value=True)
def test_copy_is_called(exists_mock, copy_mock):
    backup("/home/you/notes.txt")
    copy_mock.assert_called_once_with("/home/you/notes.txt", "/home/you/notes.txt.bak")
```

Careful: with stacked decorators the **bottom** one gives the **first** mock argument.

**How this is checked.** Your `solution.py` is a file of pytest tests. The checker copies it next
to the code above (saved as `target.py`) and runs real pytest, first on the **correct** code (all
your tests must pass), then on several **buggy copies** (at least one of your tests must fail on
each; the report names any bug that survives). To try your tests yourself, save the code as
`target.py` in your folder and run `python -m pytest solution.py -p no:cacheprovider`.
