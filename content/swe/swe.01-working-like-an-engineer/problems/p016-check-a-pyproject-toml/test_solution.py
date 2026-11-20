from solution import check_pyproject

GOOD = """[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "pricekit"
version = "0.1.0"
description = "Small price helpers: tax and discounts."
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "mypy>=1.10", "ruff>=0.5"]

[tool.setuptools.package-data]
pricekit = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests", "src"]
pythonpath = ["src"]
addopts = "-ra -q --doctest-modules"

[tool.ruff]
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src"]
"""
FILES = ["README.md", "pyproject.toml", "tasks.py", "src/pricekit/__init__.py", "src/pricekit/core.py",
         "src/pricekit/py.typed", "tests/test_core.py"]


def test_the_chapter_project_is_clean():
    assert check_pyproject(GOOD, FILES) == [], "The pyproject of chapter section 17.4 with these files has no problem."


def test_example_of_the_statement():
    assert check_pyproject('[project]\nname = "x"\n', ["x.py"]) == [
        "missing project.version", "missing project.requires-python", "no package under src/"]


def test_invalid_toml_returns_only_that():
    assert check_pyproject("[project\nname = ", FILES) == ["invalid TOML"]


def test_empty_file_reports_everything_required():
    assert check_pyproject("", FILES) == [
        "missing project.name", "missing project.version", "missing project.requires-python"], (
        "An empty file has no [project] table: do not crash, report the three missing keys.")


def test_dynamic_version_is_fine():
    text = GOOD.replace('version = "0.1.0"\n', 'dynamic = ["version"]\n')
    assert check_pyproject(text, FILES) == [], "A version listed in 'dynamic' is not missing."


def test_flat_layout_has_no_src_package():
    files = ["pricekit/__init__.py", "tests/test_core.py"]
    text = GOOD.replace('testpaths = ["tests", "src"]', 'testpaths = ["tests"]')
    assert check_pyproject(text, files) == ["no package under src/"]


def test_testpaths_folder_missing():
    got = check_pyproject(GOOD, [f for f in FILES if not f.startswith("tests/")])
    assert got == ["testpaths folder missing: tests"], f"Got {got}."
    text = GOOD.replace('["tests", "src"]', '["tests/", "docs"]')
    got = check_pyproject(text, FILES)
    assert got == ["testpaths folder missing: docs"], "An entry 'tests/' with a slash also counts as present."


def test_ruff_configured_twice():
    assert check_pyproject(GOOD, FILES + ["ruff.toml"]) == ["ruff is configured twice (pyproject.toml and ruff.toml)"]
    assert check_pyproject(GOOD, FILES + [".ruff.toml"]) == ["ruff is configured twice (pyproject.toml and ruff.toml)"]
    no_ruff = GOOD.replace('[tool.ruff]\nline-length = 88\nsrc = ["src", "tests"]\n\n[tool.ruff.lint]\nselect = ["E", "F", "I", "B", "UP"]\n\n', "")
    assert "[tool.ruff" not in no_ruff
    assert check_pyproject(no_ruff, FILES + ["ruff.toml"]) == [], "A ruff.toml alone is fine."


def test_dependencies_need_a_lower_bound():
    text = GOOD.replace("dependencies = []", 'dependencies = ["requests", "rich>=13", "click<9", "numpy==1.26.0", "attrs~=23.1"]')
    assert check_pyproject(text, FILES) == [
        "dependency without a lower bound: requests", "dependency without a lower bound: click<9"], (
        "'requests' has no version; 'click<9' only an upper bound. '>=', '==' and '~=' count as lower bounds.")
    text = GOOD.replace('dev = ["pytest>=8", "mypy>=1.10", "ruff>=0.5"]', 'dev = ["pytest", "mypy>=1.10"]')
    assert check_pyproject(text, FILES) == ["dependency without a lower bound: pytest"], (
        "Optional dependency groups are checked too.")


def test_several_problems_in_table_order():
    text = '[project]\ndependencies = ["x"]\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n[tool.ruff]\nline-length = 88\n'
    assert check_pyproject(text, ["ruff.toml"]) == [
        "missing project.name", "missing project.version", "missing project.requires-python",
        "no package under src/", "testpaths folder missing: tests",
        "ruff is configured twice (pyproject.toml and ruff.toml)", "dependency without a lower bound: x"]
