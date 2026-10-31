import traceback

import pytest

from solution import blame

SIMPLE = '''Traceback (most recent call last):
  File "/home/you/shop.py", line 14, in <module>
    main()
  File "/home/you/shop.py", line 10, in main
    print(price("pen"))
          ~~~~~^^^^^^^
  File "/home/you/shop.py", line 6, in price
    return PRICES[name] * 1.18
           ~~~~~~^^^^^^
KeyError: 'pen'
'''

CHAINED = '''Traceback (most recent call last):
  File "/home/you/cfg.py", line 3, in load
    return int(text)
ValueError: invalid literal for int() with base 10: 'abc'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/you/cfg.py", line 9, in <module>
    load("abc")
  File "/home/you/cfg.py", line 5, in load
    raise RuntimeError("bad config")
RuntimeError: bad config
'''

CAUSE = '''Traceback (most recent call last):
  File "/home/you/app/db.py", line 40, in connect
    sock.connect(addr)
ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/you/app/main.py", line 7, in <module>
    run()
  File "/home/you/app/main.py", line 4, in run
    db.open()
  File "/home/you/app/db.py", line 52, in open
    raise DatabaseError("cannot open") from exc
app.db.DatabaseError: cannot open
'''

TRICKY_SOURCE = '''Traceback (most recent call last):
  File "C:\\Users\\you\\report.py", line 21, in <module>
    write_report()
  File "C:\\Users\\you\\report.py", line 17, in write_report
    log("disk full")
  File "C:\\Users\\you\\report.py", line 12, in log
    raise OSError('  File "fake.py", line 99, in nowhere')
OSError:   File "fake.py", line 99, in nowhere
'''


SYNTAX = '''Traceback (most recent call last):
  File "/home/you/run.py", line 2, in <module>
    import broken
  File "/home/you/broken.py", line 3
    if x = 1:
       ^^^^^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
'''


def test_innermost_frame_is_the_last_one():
    assert blame(SIMPLE) == ("/home/you/shop.py", 6, "price"), (
        "Frames are listed outermost first, so the line that raised is the LAST 'File' line. "
        "Did you take the first one (<module>)?"
    )


def test_chained_tracebacks_use_the_last_block():
    assert blame(CHAINED) == ("/home/you/cfg.py", 5, "load"), (
        "With 'During handling ...' the exception that reached you is printed LAST. "
        "Line 3 is the old ValueError; the answer is line 5 of the last block."
    )
    assert blame(CAUSE) == ("/home/you/app/db.py", 52, "open"), (
        "'raise ... from exc' also prints two tracebacks. Take the innermost frame of the last one."
    )


def test_line_is_an_int():
    _, line, _ = blame(SIMPLE)
    assert type(line) is int, f"Return the line number as an int, not {type(line).__name__}."


def test_source_lines_are_not_frames():
    assert blame(TRICKY_SOURCE) == ("C:\\Users\\you\\report.py", 12, "log"), (
        "The source line and the error message contain 'File \"fake.py\", line 99'. Only lines "
        "that START with exactly two spaces then 'File' are frames: anchor your pattern with ^ "
        "and re.MULTILINE."
    )


def test_syntax_error_frame_has_no_function():
    assert blame(SYNTAX) == ("/home/you/broken.py", 3, ""), (
        "A SyntaxError frame line has no ', in <function>' part. Make that part optional and "
        "return '' for the function, instead of skipping to an earlier frame."
    )


def test_no_frames_raises_value_error():
    with pytest.raises(ValueError):
        blame("KeyError: 'pen'\n")
    with pytest.raises(ValueError):
        blame("")


def _inner():
    raise LookupError("deep")


def _outer():
    try:
        {}["missing"]
    except KeyError:
        _inner()


def test_real_traceback_from_python():
    try:
        _outer()
    except LookupError:
        text = traceback.format_exc()
    file, line, function = blame(text)
    assert function == "_inner", (
        f"On a real chained traceback the innermost frame of the last block is _inner, got {function!r}."
    )
    assert file.endswith("test_solution.py"), f"File should be the test file, got {file!r}."
    assert line == _inner.__code__.co_firstlineno + 1, "The line should be the 'raise' inside _inner."
