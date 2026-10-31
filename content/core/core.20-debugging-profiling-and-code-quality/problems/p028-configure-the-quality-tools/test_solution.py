import tomllib

import pytest
import yaml

import solution


@pytest.fixture
def py():
    try:
        return tomllib.loads(solution.PYPROJECT)
    except tomllib.TOMLDecodeError as e:
        raise AssertionError(f"PYPROJECT is not valid TOML: {e}. Check quotes around strings and the [table] headers.") from None


@pytest.fixture
def pc():
    try:
        data = yaml.safe_load(solution.PRECOMMIT)
    except yaml.YAMLError as e:
        raise AssertionError(f"PRECOMMIT is not valid YAML: {e}. Check the indentation (spaces only, no tabs).") from None
    assert isinstance(data, dict) and "repos" in data, "PRECOMMIT must have a top-level key 'repos'."
    return data


def tool(py, *path):
    node = py.get("tool", {})
    for key in path:
        assert isinstance(node, dict) and key in node, f"Missing [tool.{'.'.join(path)}] (stopped at '{key}')."
        node = node[key]
    return node


def test_ruff_basics(py):
    ruff = tool(py, "ruff")
    assert ruff.get("line-length") == 100, "[tool.ruff] line-length = 100 (a number, no quotes; the key uses a dash)."
    assert ruff.get("target-version") == "py311", 'target-version = "py311" (a string).'


def test_ruff_lint(py):
    lint = tool(py, "ruff", "lint")
    assert sorted(lint.get("select", [])) == sorted(["E", "F", "W", "I", "B", "UP"]), (
        f"select is {lint.get('select')}. It must be exactly E, F, W, I, B, UP. Since ruff 0.2 select/ignore "
        "belong in [tool.ruff.lint], not [tool.ruff]."
    )
    assert lint.get("ignore") == ["E501"], 'ignore = ["E501"] (a list, even with one item).'


def test_per_file_ignores(py):
    pfi = tool(py, "ruff", "lint", "per-file-ignores")
    assert pfi == {"__init__.py": ["F401"]}, f'per-file-ignores is {pfi}. Expected "__init__.py" = ["F401"] (quote the key: it contains a dot).'


def test_ruff_format(py):
    assert tool(py, "ruff", "format").get("quote-style") == "double", '[tool.ruff.format] quote-style = "double".'


def test_mypy(py):
    mypy = tool(py, "mypy")
    assert mypy.get("strict") is True, "strict = true (a TOML boolean: lowercase, no quotes)."
    assert mypy.get("python_version") == "3.11", 'python_version = "3.11" as a STRING; unquoted 3.11 is a float and mypy rejects it.'
    assert mypy.get("files") == ["src", "tests"], 'files = ["src", "tests"].'


def test_mypy_overrides_is_array_of_tables(py):
    overrides = tool(py, "mypy", "overrides")
    assert isinstance(overrides, list) and len(overrides) == 1, (
        f"overrides is {overrides!r}. Use [[tool.mypy.overrides]] (double brackets): it is a LIST of tables."
    )
    entry = overrides[0]
    assert entry.get("module") == ["yaml", "yaml.*"] and entry.get("ignore_missing_imports") is True, (
        f"Got {entry}. The entry needs module = [\"yaml\", \"yaml.*\"] and ignore_missing_imports = true."
    )


def test_pytest_options(py):
    opts = tool(py, "pytest", "ini_options")
    assert opts.get("testpaths") == ["tests"] and opts.get("addopts") == "-q", 'testpaths = ["tests"] and addopts = "-q" under [tool.pytest.ini_options].'


def hooks_of(repo):
    return [h.get("id") for h in repo.get("hooks", [])]


def test_repo_order(pc):
    urls = [r.get("repo") for r in pc["repos"]]
    assert urls == ["https://github.com/astral-sh/ruff-pre-commit", "https://github.com/pre-commit/mirrors-mypy", "local"], (
        f"repos are {urls}. Expected ruff-pre-commit, then mirrors-mypy, then local (cheap fixers first, tests last)."
    )


def test_revs_are_v_strings(pc):
    for repo in pc["repos"]:
        if repo.get("repo") == "local":
            assert "rev" not in repo, "A local repo has no rev."
            continue
        rev = repo.get("rev")
        assert isinstance(rev, str) and rev.startswith("v"), (
            f"rev for {repo.get('repo')} is {rev!r}. It must be a string like v0.6.9; without the v, YAML may read "
            "a value like 1.10 as the float 1.1."
        )


def test_ruff_hooks(pc):
    ruff = pc["repos"][0]
    assert hooks_of(ruff) == ["ruff", "ruff-format"], f"Ruff hooks are {hooks_of(ruff)}: lint (ruff) must come BEFORE ruff-format."
    assert ruff["hooks"][0].get("args") == ["--fix"], "The ruff hook needs args: [--fix] (a YAML list)."


def test_mypy_hook(pc):
    mypy = pc["repos"][1]
    assert hooks_of(mypy) == ["mypy"], f"mirrors-mypy must have exactly the hook mypy, got {hooks_of(mypy)}."
    assert mypy["hooks"][0].get("additional_dependencies") == ["types-PyYAML"], "mypy needs additional_dependencies: [types-PyYAML]."


def test_local_pytest_hook(pc):
    local = pc["repos"][2]
    assert hooks_of(local) == ["pytest"], f"The local repo must have one hook with id pytest, got {hooks_of(local)}."
    hook = local["hooks"][0]
    expected = {"name": "pytest", "entry": "pytest -q", "language": "system", "types": ["python"]}
    for key, value in expected.items():
        assert hook.get(key) == value, f"pytest hook: {key} should be {value!r}, got {hook.get(key)!r}."
    assert hook.get("pass_filenames") is False, (
        f"pass_filenames is {hook.get('pass_filenames')!r}. It must be the YAML boolean false (no quotes), so pytest "
        "runs the whole suite instead of being handed the changed file names."
    )
