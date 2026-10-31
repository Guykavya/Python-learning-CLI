from pathlib import Path

from solution import parse_requirements

FIXTURE = Path(__file__).parent / "fixtures" / "requirements.txt"


def write(tmp_path, text):
    p = tmp_path / "requirements.txt"
    p.write_text(text, encoding="utf-8")
    return p


def test_fixture_example():
    assert parse_requirements(FIXTURE) == [
        ("requests", ">=2.31,<3"),
        ("flask", "==3.0.2"),
        ("python-dateutil", ""),
        ("numpy", ">=1.26"),
        ("uvicorn", "~=0.29"),
        ("django-rest-framework", "!=3.14.0"),
    ], "Compare your list with the example line by line: comments, options, markers, extras and names."


def test_simple_pin(tmp_path):
    p = write(tmp_path, "flask==3.0.2\n")
    assert parse_requirements(str(p)) == [("flask", "==3.0.2")], "Split the line into the name and the specifier."


def test_comments_and_blank_lines(tmp_path):
    p = write(tmp_path, "# only a comment\n\n   \nrich  # pretty output\n")
    assert parse_requirements(p) == [("rich", "")], (
        "Drop text after '#', then skip lines that are empty. A name with no specifier has spec ''."
    )


def test_options_skipped(tmp_path):
    p = write(tmp_path, "-r base.txt\n-e .\n--index-url https://x.org/simple\n-c constraints.txt\nattrs\n")
    assert parse_requirements(p) == [("attrs", "")], "Lines that start with '-' are pip options, not packages. Skip them."


def test_name_normalised(tmp_path):
    p = write(tmp_path, "Typing_Extensions>=4\nzope.interface\nPyYAML\n")
    assert parse_requirements(p) == [
        ("typing-extensions", ">=4"),
        ("zope-interface", ""),
        ("pyyaml", ""),
    ], "Normalise names: lowercase, and '_' and '.' become '-'."


def test_spaces_removed_from_spec(tmp_path):
    p = write(tmp_path, "pandas >= 2.0 , < 3.0\n")
    assert parse_requirements(p) == [("pandas", ">=2.0,<3.0")], "Remove every space from the specifier, also around the comma."


def test_marker_dropped(tmp_path):
    p = write(tmp_path, 'tomli>=2 ; python_version < "3.11"\n')
    assert parse_requirements(p) == [("tomli", ">=2")], "Everything from ';' is an environment marker. Drop it."


def test_extras_dropped(tmp_path):
    p = write(tmp_path, "requests[socks,security]==2.31.0\nfastapi[all]\n")
    assert parse_requirements(p) == [("requests", "==2.31.0"), ("fastapi", "")], (
        "Extras in [...] after the name are not part of the name or the specifier."
    )


def test_order_kept(tmp_path):
    p = write(tmp_path, "b\na\nc\n")
    assert [n for n, _ in parse_requirements(p)] == ["b", "a", "c"], "Keep the file order. Do not sort."


def test_empty_file(tmp_path):
    p = write(tmp_path, "")
    assert parse_requirements(p) == [], "An empty file gives an empty list."
