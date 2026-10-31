import importlib
import os
import subprocess
import sys
import tomllib

import pytest

from solution import make_project, package_name

PACKAGES = ("word_tools", "word_tools_2", "a_tool", "b_tool", "texty")


def drop_packages():
    for name in list(sys.modules):
        if name.split(".")[0] in PACKAGES:
            del sys.modules[name]


@pytest.fixture(autouse=True)
def clean_modules():
    drop_packages()
    yield
    drop_packages()


@pytest.fixture
def project(tmp_path):
    return make_project(tmp_path, "word-tools")


def load_toml(project_dir):
    with open(project_dir / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def use_src(monkeypatch, project_dir):
    monkeypatch.syspath_prepend(str(project_dir / "src"))
    importlib.invalidate_caches()


def run(project_dir, args, stdin=""):
    """Run python with PYTHONPATH=src, like an installed package, but without installing."""
    env = dict(os.environ, PYTHONPATH=str(project_dir / "src"), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, *args], cwd=project_dir, input=stdin, env=env,
                          capture_output=True, text=True, timeout=30)


# ------------------------------------------------------------------ layout and names

def test_returns_project_folder(tmp_path):
    result = make_project(tmp_path, "word-tools")
    assert result == tmp_path / "word-tools", "make_project returns the Path of the new project folder: root / name."


def test_src_layout(project):
    expected = {"pyproject.toml", "README.md", "src/word_tools/__init__.py", "src/word_tools/core.py",
                "src/word_tools/cli.py", "src/word_tools/__main__.py", "tests/test_core.py"}
    found = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file()}
    assert expected <= found, f"Missing files: {sorted(expected - found)}. Use the src layout: the package lives in src/<package>/."
    assert not (project / "word_tools").exists(), "No package folder at the top of the project. That is the flat layout; put it under src/."


@pytest.mark.parametrize("name, package", [("word-tools", "word_tools"), ("Word.Tools_2", "word_tools_2"),
                                           ("texty", "texty"), ("a--b..c", "a_b_c")])
def test_package_name(name, package):
    assert package_name(name) == package, f"package_name({name!r}) should be {package!r}: lowercase, and each run of - _ . becomes ONE underscore."


def test_derived_package_folder(tmp_path):
    project = make_project(tmp_path, "Word.Tools_2")
    assert (project / "src" / "word_tools_2" / "__init__.py").is_file(), "Without package=..., the import name comes from package_name(name)."


def test_custom_package(tmp_path):
    project = make_project(tmp_path, "my-text-kit", package="texty")
    assert (project / "src" / "texty" / "cli.py").is_file(), "package=... overrides the import name."
    assert load_toml(project)["project"]["scripts"]["my-text-kit"] == "texty.cli:main", "The entry point uses the package name, the command uses the project name."


@pytest.mark.parametrize("bad", ["", "-tool", "tool-", "has space", "naïve", "a/b"])
def test_invalid_project_name(tmp_path, bad):
    with pytest.raises(ValueError):
        make_project(tmp_path, bad)
    assert list(tmp_path.iterdir()) == [], "Check the arguments before you create anything."


@pytest.mark.parametrize("name, package", [("1st-tool", None), ("tool", "class"), ("tool", "my-pkg")])
def test_invalid_package_name(tmp_path, name, package):
    with pytest.raises(ValueError):
        make_project(tmp_path, name, package=package)
    assert list(tmp_path.iterdir()) == [], "An import name must be a valid identifier and not a keyword (str.isidentifier, keyword.iskeyword). Check before writing."


@pytest.mark.parametrize("bad", ["", "1.x", "v1.0", "1..0"])
def test_invalid_version(tmp_path, bad):
    with pytest.raises(ValueError):
        make_project(tmp_path, "word-tools", version=bad)


def test_never_overwrites(tmp_path):
    existing = tmp_path / "word-tools"
    existing.mkdir()
    (existing / "notes.txt").write_text("keep me", encoding="utf-8")
    with pytest.raises(FileExistsError):
        make_project(tmp_path, "word-tools")
    assert [p.name for p in existing.iterdir()] == ["notes.txt"], "A folder that is not empty must not be touched."


def test_empty_existing_folder_is_fine(tmp_path):
    (tmp_path / "word-tools").mkdir()
    project = make_project(tmp_path, "word-tools")
    assert (project / "pyproject.toml").is_file(), "An existing EMPTY folder may be used."


# ------------------------------------------------------------------ pyproject.toml

def test_pyproject_is_valid_toml(project):
    try:
        load_toml(project)
    except tomllib.TOMLDecodeError as e:
        pytest.fail(f"pyproject.toml is not valid TOML: {e}")


def test_build_system(project):
    data = load_toml(project)
    bs = data.get("build-system", {})
    assert any(r.replace(" ", "").startswith("setuptools") for r in bs.get("requires", [])), "[build-system] requires must list setuptools (for example 'setuptools>=61')."
    assert bs.get("build-backend") == "setuptools.build_meta", "build-backend is 'setuptools.build_meta'."


def test_project_table(tmp_path):
    project = make_project(tmp_path, "word-tools", version="1.2.0", requires_python=">=3.11",
                           dependencies=["rich>=13", "click==8.1.7"])
    p = load_toml(project)["project"]
    assert p["name"] == "word-tools", "[project] name is the project (distribution) name."
    assert p["version"] == "1.2.0", "[project] version comes from the version argument."
    assert p["requires-python"] == ">=3.11", "requires-python comes from the argument."
    assert p["dependencies"] == ["rich>=13", "click==8.1.7"], "dependencies is a TOML array of strings, in the given order."
    assert p.get("readme") == "README.md", "Point readme at README.md."


def test_defaults(project):
    p = load_toml(project)["project"]
    assert (p["version"], p["requires-python"], p["dependencies"]) == ("0.1.0", ">=3.10", []), "Defaults: version 0.1.0, requires-python >=3.10, no dependencies (an empty array)."


def test_strings_are_escaped(tmp_path):
    desc = 'Says "hi" with a back\\slash'
    deps = ['tomli>=2; python_version < "3.11"']
    project = make_project(tmp_path, "word-tools", description=desc, dependencies=deps)
    p = load_toml(project)["project"]
    assert p["description"] == desc, "Quotes and backslashes must be escaped in TOML strings. json.dumps(text) gives a valid TOML basic string."
    assert p["dependencies"] == deps, "A dependency with an environment marker contains quotes too. Escape it."


def test_scripts_entry(project):
    scripts = load_toml(project)["project"].get("scripts", {})
    assert scripts == {"word-tools": "word_tools.cli:main"}, "[project.scripts] maps the command name to 'package.cli:main'."


def test_setuptools_finds_src(project):
    find = load_toml(project).get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {})
    assert find.get("where") == ["src"], "Tell setuptools where the code is: [tool.setuptools.packages.find] where = [\"src\"]."


# ------------------------------------------------------------------ the package

def test_import_package(project, monkeypatch, capsys):
    use_src(monkeypatch, project)
    import word_tools
    assert capsys.readouterr().out == "", "Importing the package must print nothing."
    assert word_tools.__version__ == "0.1.0", "__init__.py sets __version__ to the same version as pyproject.toml."
    assert sorted(word_tools.__all__) == ["slugify", "word_count"], "__all__ lists the public API: slugify and word_count."
    assert word_tools.slugify.__module__ == "word_tools.core", "slugify lives in core.py; __init__.py re-exports it."


def test_version_matches(tmp_path, monkeypatch):
    project = make_project(tmp_path, "word-tools", version="2.5")
    use_src(monkeypatch, project)
    import word_tools
    assert word_tools.__version__ == load_toml(project)["project"]["version"] == "2.5", "One version, written in both places from the same argument."


@pytest.mark.parametrize("text, slug", [("Hello, World!", "hello-world"), ("  many   spaces  ", "many-spaces"),
                                        ("Snake_case And-Dash", "snake-case-and-dash"), ("!!!", ""),
                                        ("Python 3.13 is out", "python-3-13-is-out")])
def test_slugify(project, monkeypatch, text, slug):
    use_src(monkeypatch, project)
    from word_tools import slugify
    assert slugify(text) == slug, f"slugify({text!r}) should be {slug!r}: lowercase, keep letters and digits, every run of other characters becomes one '-', no '-' at the ends."


def test_word_count(project, monkeypatch):
    use_src(monkeypatch, project)
    from word_tools import word_count
    assert word_count("one two  three\n") == 3 and word_count("") == 0, "word_count is len(text.split())."


def test_entry_point_resolves(project, monkeypatch, capsys):
    use_src(monkeypatch, project)
    target = load_toml(project)["project"]["scripts"]["word-tools"]
    module_name, _, func_name = target.partition(":")
    func = getattr(importlib.import_module(module_name), func_name)
    assert callable(func), "The entry point must point at a callable."
    assert func(["slug", "Hello", "World"]) == 0, "main(argv) returns 0 on success (the console script does sys.exit(main()))."
    assert capsys.readouterr().out == "hello-world\n", "slug joins its words with spaces and prints the slug."


def test_main_reads_argv_list(project, monkeypatch, capsys):
    use_src(monkeypatch, project)
    from word_tools.cli import main
    f = project / "words.txt"
    f.write_text("a b c d\n", encoding="utf-8")
    assert main(["count", str(f)]) == 0, "count FILE returns 0."
    assert capsys.readouterr().out == "4\n", "count prints the number of words in the file."


# ------------------------------------------------------------------ python -m

def test_python_m_help(project):
    proc = run(project, ["-m", "word_tools", "--help"])
    assert proc.returncode == 0, f"python -m word_tools --help failed. Is there a src/word_tools/__main__.py?\n{proc.stderr[-500:]}"
    assert proc.stdout.startswith("usage: word-tools"), "Set argparse prog to the command name, so help says 'usage: word-tools ...'."
    assert "slug" in proc.stdout and "count" in proc.stdout, "The help lists the two sub-commands slug and count."


def test_python_m_version(project):
    proc = run(project, ["-m", "word_tools", "--version"])
    assert (proc.returncode, proc.stdout) == (0, "word-tools 0.1.0\n"), "--version prints 'word-tools 0.1.0' (argparse action='version') and exits 0."


def test_python_m_slug(project):
    proc = run(project, ["-m", "word_tools", "slug", "Packaging", "is", "FUN!"])
    assert (proc.returncode, proc.stdout) == (0, "packaging-is-fun\n"), "python -m word_tools slug WORDS... prints the slug. __main__.py calls main() under if __name__ == '__main__'."


def test_python_m_count_stdin(project):
    proc = run(project, ["-m", "word_tools", "count"], stdin="one two\nthree\n")
    assert (proc.returncode, proc.stdout) == (0, "3\n"), "count with no file (or '-') reads stdin."
    proc = run(project, ["-m", "word_tools", "count", "-"], stdin="x y\n")
    assert proc.stdout == "2\n", "count - also reads stdin."


def test_python_m_missing_file(project):
    proc = run(project, ["-m", "word_tools", "count", "nope.txt"])
    assert proc.returncode == 1, "A file that cannot be read gives exit code 1. __main__.py must pass main()'s return value to sys.exit."
    assert proc.stdout == "" and proc.stderr.startswith("error:"), "Print 'error: ...' to stderr, nothing to stdout, no traceback."


def test_python_m_no_command(project):
    proc = run(project, ["-m", "word_tools"])
    assert proc.returncode == 2, "No sub-command is a usage error: exit code 2 (add_subparsers(required=True))."


def test_cli_is_not_run_on_import(project):
    proc = run(project, ["-c", "import word_tools.cli, word_tools.__main__"])
    assert (proc.returncode, proc.stdout) == (0, ""), "Importing cli or __main__ must not run the program. Guard the call with if __name__ == '__main__'."


# ------------------------------------------------------------------ tests and README

def test_generated_tests_pass(project):
    proc = run(project, ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"])
    assert proc.returncode == 0, f"The project's own tests (tests/test_core.py) must pass:\n{proc.stdout[-800:]}"
    assert " passed" in proc.stdout and "no tests ran" not in proc.stdout, "tests/test_core.py must contain real tests."


def test_readme(project):
    text = (project / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# word-tools"), "The README starts with a '# <name>' heading."
    assert "pip install" in text, "The README says how to install the project."
    assert "word-tools slug" in text, "The README shows how to use the command."


def test_two_projects_side_by_side(tmp_path, monkeypatch):
    a = make_project(tmp_path, "a-tool")
    b = make_project(tmp_path, "b-tool", version="0.2.0")
    use_src(monkeypatch, a)
    use_src(monkeypatch, b)
    import a_tool
    import b_tool
    assert (a_tool.__version__, b_tool.__version__) == ("0.1.0", "0.2.0"), "Every project gets its own package and version. Do not use module-level state that leaks between calls."
    proc = run(b, ["-m", "b_tool", "--version"])
    assert proc.stdout == "b-tool 0.2.0\n", "The generated CLI uses this project's name and version."
