import io

import pytest

from solution import Lines, count_nonblank, first_line

CODE = "import os\n\n# setup\nx = 1\n   \nprint(x)\n"


class OnlyIter:
    """A source written by 'someone else': it only has __iter__."""

    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)


class Endless:
    """Gives blank lines, one real line, then fails if read any further."""

    def __init__(self):
        self.reads = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.reads += 1
        if self.reads < 3:
            return "   \n"
        if self.reads == 3:
            return "  found it \n"
        raise AssertionError("first_line read past the first non-blank line; return as soon as you find it.")


def test_list_of_lines():
    assert count_nonblank(CODE.splitlines()) == 4, "Blank lines and lines of only spaces are not counted; '# setup' is (no comment given)."


def test_lines_with_newlines():
    assert count_nonblank(["a\n", "\n", "  \n", "b\n"]) == 2, "Lines may end with '\\n'; strip() removes it."


def test_stringio_and_comment():
    assert count_nonblank(io.StringIO(CODE)) == 4, "An io.StringIO gives its lines when you loop over it."
    assert count_nonblank(io.StringIO(CODE), comment="#") == 3, "With comment='#', skip '# setup'."
    assert count_nonblank(["  // note", "x", "//"], comment="//") == 1, "Check the comment after strip(); any marker works."


def test_generator_and_tuple():
    assert count_nonblank(line for line in ["a", "", "b"]) == 2, "A generator is fine: just loop over it once."
    assert count_nonblank(("x", "y")) == 2, "A tuple is fine too."


def test_any_class_with_iter():
    assert count_nonblank(OnlyIter(["a", " ", "b", "c"])) == 3, (
        "Do not check the type of source (list, file ...). Any object you can loop over must work."
    )


def test_file(tmp_path):
    p = tmp_path / "code.py"
    p.write_text(CODE, encoding="utf-8")
    with open(p, encoding="utf-8") as f:
        assert count_nonblank(f, comment="#") == 3, "An open file gives its lines when you loop over it."


def test_string_is_rejected():
    try:
        result = count_nonblank(CODE)
    except TypeError as e:
        assert "lines" in str(e), "The TypeError message should mention lines, e.g. 'pass lines, not one string'."
    else:
        pytest.fail(
            f"count_nonblank(one string) returned {result}. Looping over a str gives characters, not lines: "
            "raise TypeError for a str."
        )
    with pytest.raises(TypeError):
        count_nonblank("abc")


def test_not_iterable():
    with pytest.raises(TypeError):
        count_nonblank(42)


def test_empty():
    assert count_nonblank([]) == 0, "No lines, count 0."


def test_first_line():
    assert first_line(["", "  ", "  hello  ", "world"]) == "hello", "The first non-blank line, stripped."
    assert first_line([]) is None, "No lines: None."
    assert first_line(["", "   "]) is None, "Only blank lines: None."
    assert first_line(io.StringIO("\n\nx = 1\n")) == "x = 1", "Works with any source of lines."


def test_first_line_stops_early():
    src = Endless()
    assert first_line(src) == "found it", "Return the first non-blank line."
    assert src.reads == 3, "Stop reading as soon as you find it."


def test_lines_class():
    lines = Lines(CODE)
    assert list(lines) == ["import os", "", "# setup", "x = 1", "   ", "print(x)"], (
        "Looping over Lines gives text.splitlines(), one line at a time."
    )
    assert count_nonblank(lines) == 4, "count_nonblank works with a Lines object."
    assert count_nonblank(lines, comment="#") == 3, (
        "A Lines object can be looped over again and again. Make __iter__ start fresh each time (a generator method does)."
    )
    assert first_line(Lines("\n\n  top\nnext")) == "top", "first_line works with Lines too."


def test_lines_empty():
    assert list(Lines("")) == [], "Empty text has no lines."
