import pytest

from solution import resolve

MENU = (
    'PRICES = {\n'
    '<<<<<<< HEAD\n'
    '    "tea": 15,\n'
    '=======\n'
    '    "tea": 25,\n'
    '>>>>>>> feature\n'
    '    "coffee": 30,\n'
    '    "cake": 50,\n'
    '}\n'
)


def test_ours_theirs_both():
    assert resolve(MENU, "ours") == 'PRICES = {\n    "tea": 15,\n    "coffee": 30,\n    "cake": 50,\n}\n'
    assert resolve(MENU, "theirs") == 'PRICES = {\n    "tea": 25,\n    "coffee": 30,\n    "cake": 50,\n}\n'
    assert resolve(MENU, "both") == 'PRICES = {\n    "tea": 15,\n    "tea": 25,\n    "coffee": 30,\n    "cake": 50,\n}\n', (
        "'both' keeps our lines first, then theirs.")


def test_no_marker_line_is_left():
    for how in ("ours", "theirs", "both"):
        out = resolve(MENU, how)
        assert "<<<<<<<" not in out and ">>>>>>>" not in out and "=======" not in out, f"'{how}' left a marker line."


def test_several_blocks():
    text = "a\n<<<<<<< HEAD\n1\n=======\n2\n>>>>>>> x\nb\n<<<<<<< HEAD\n3\n4\n=======\n5\n>>>>>>> x\nc\n"
    assert resolve(text, "ours") == "a\n1\nb\n3\n4\nc\n"
    assert resolve(text, "theirs") == "a\n2\nb\n5\nc\n", "Every block must be resolved, not only the first."


def test_function_chooser_gets_the_two_sides():
    seen = []

    def pick_longer(ours, theirs):
        seen.append((ours, theirs))
        return ours if len(ours) >= len(theirs) else theirs

    text = "<<<<<<< HEAD\nx\ny\n=======\nz\n>>>>>>> b\nend\n"
    assert resolve(text, pick_longer) == "x\ny\nend\n"
    assert seen == [(["x", "y"], ["z"])], "Call the function once per block, with the lists of lines of both sides."


def test_empty_side():
    text = "a\n<<<<<<< HEAD\n=======\nnew\n>>>>>>> b\nz\n"
    assert resolve(text, "ours") == "a\nz\n", "One side may be empty (one branch deleted the lines)."
    assert resolve(text, "theirs") == "a\nnew\nz\n"


def test_text_without_markers_is_unchanged():
    for t in ("", "plain\ntext\n", "no newline at the end", "Title\n=======\nBody\n"):
        assert resolve(t, "ours") == t, "A file without markers must come back exactly as it was (even '=======')."


def test_final_newline_is_kept_or_absent():
    assert resolve("<<<<<<< HEAD\na\n=======\nb\n>>>>>>> x", "ours") == "a", "No newline at the end stays so."
    assert resolve("<<<<<<< HEAD\na\n=======\nb\n>>>>>>> x\n", "ours") == "a\n"


def test_markers_without_label():
    assert resolve("<<<<<<<\na\n=======\nb\n>>>>>>>\n", "theirs") == "b\n"


def test_bad_choose():
    with pytest.raises(ValueError):
        resolve(MENU, "mine")


@pytest.mark.parametrize("text,line", [
    ("a\nb\n>>>>>>> x\n", 3),
    ("a\n<<<<<<< HEAD\nb\n<<<<<<< HEAD\nc\n", 4),
    ("a\n<<<<<<< HEAD\nb\n=======\nc\n", 2),
    ("a\nb\n<<<<<<< HEAD\nb\n>>>>>>> x\n", 5),
    ("<<<<<<< HEAD\n=======\n=======\n>>>>>>> x\n", 3),
])
def test_unbalanced_markers_name_the_line(text, line):
    with pytest.raises(ValueError) as e:
        resolve(text, "ours")
    assert f"line {line}" in str(e.value), f"The error message must name the offending line: 'line {line}'. Got: {e.value}"
