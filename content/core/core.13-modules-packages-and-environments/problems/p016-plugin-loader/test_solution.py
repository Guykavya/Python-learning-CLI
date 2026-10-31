import sys

import pytest

from solution import load_plugins, run_plugins


def write(folder, files):
    folder.mkdir(parents=True, exist_ok=True)
    for name, code in files.items():
        (folder / name).write_text(code, encoding="utf-8")
    return folder


REG = 'def register(app):\n    app.setdefault("commands", []).append("{name}")\n'


@pytest.fixture
def plugins_dir(tmp_path):
    return write(tmp_path / "plugins", {
        "upper.py": REG.format(name="upper"),
        "greet.py": REG.format(name="greet"),
        "notes.py": "VALUE = 3\n",
        "_shared.py": REG.format(name="shared"),
        "__init__.py": REG.format(name="init"),
        "broken.py": "x = 1 / 0\n",
    })


def test_finds_register_functions(plugins_dir):
    plugins, failed = load_plugins(plugins_dir)
    assert list(plugins) == ["greet", "upper"], "Collect the stems of public files that define register, in sorted order. Skip names starting with '_' and modules without register."
    assert all(callable(f) for f in plugins.values()), "The dict values are the register functions themselves (not their names or the modules)."


def test_failed_plugins_are_listed(plugins_dir):
    plugins, failed = load_plugins(plugins_dir)
    assert failed == ["broken"], "A file whose top-level code raises must not crash the loader. Catch Exception around exec_module and add the stem to failed."


def test_str_path_works(plugins_dir):
    plugins, failed = load_plugins(str(plugins_dir))
    assert list(plugins) == ["greet", "upper"], "folder may be a str. Wrap it in Path(...)."


def test_syntax_error_is_a_failure(tmp_path):
    folder = write(tmp_path / "p", {"bad.py": "def register(app)\n    pass\n", "ok.py": REG.format(name="ok")})
    plugins, failed = load_plugins(folder)
    assert (list(plugins), failed) == (["ok"], ["bad"]), "A SyntaxError is raised by exec_module too. It is an Exception, so the file goes into failed."


def test_register_must_be_callable(tmp_path):
    folder = write(tmp_path / "p", {"five.py": "register = 5\n", "real.py": REG.format(name="real")})
    plugins, failed = load_plugins(folder)
    assert list(plugins) == ["real"] and failed == [], "register = 5 is not a plugin. Check callable(...) before you collect it, and it is not a failure either."


def test_ignores_subfolders_and_other_files(tmp_path):
    folder = write(tmp_path / "p", {"a.py": REG.format(name="a"), "readme.txt": "hi", "notes.md": "x"})
    write(folder / "deeper", {"b.py": REG.format(name="b")})
    plugins, failed = load_plugins(folder)
    assert list(plugins) == ["a"], "Only .py files directly in the folder are plugins. Use folder.glob('*.py'), not rglob."


def test_sorted_order(tmp_path):
    names = ["zeta", "alpha", "mid", "beta"]
    folder = write(tmp_path / "p", {f"{n}.py": REG.format(name=n) for n in names})
    plugins, _ = load_plugins(folder)
    assert list(plugins) == sorted(names), "Return the plugins in sorted order of their names, not in the order the folder lists them."


def test_empty_folder(tmp_path):
    (tmp_path / "empty").mkdir()
    assert load_plugins(tmp_path / "empty") == ({}, []), "An empty folder gives ({}, [])."


def test_missing_folder(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_plugins(tmp_path / "nope")


def test_reloads_fresh_each_call(tmp_path):
    folder = write(tmp_path / "p", {"hello.py": 'def register(app):\n    app["v"] = 1\n'})
    app = {}
    load_plugins(folder)[0]["hello"](app)
    assert app == {"v": 1}
    (folder / "hello.py").write_text('def register(app):\n    app["v"] = 22  # new size, so no stale bytecode\n', encoding="utf-8")
    app = {}
    load_plugins(folder)[0]["hello"](app)
    assert app == {"v": 22}, "The second call must load the changed file. import_module would return the cached old module; load each file with spec_from_file_location + exec_module."


def test_does_not_touch_sys_path(plugins_dir):
    before = list(sys.path)
    load_plugins(plugins_dir)
    assert sys.path == before, "Do not add the plugin folder to sys.path. spec_from_file_location loads by path."


def test_plugins_are_separate_modules(tmp_path):
    folder = write(tmp_path / "p", {
        "one.py": 'NAME = "one"\ndef register(app):\n    app.append(NAME)\n',
        "two.py": 'NAME = "two"\ndef register(app):\n    app.append(NAME)\n',
    })
    app = []
    for f in load_plugins(folder)[0].values():
        f(app)
    assert app == ["one", "two"], "Each file must be its own module object with its own globals. Make a new module for every file."


def test_run_plugins(plugins_dir):
    app = {}
    called = run_plugins(plugins_dir, app)
    assert called == ["greet", "upper"], "run_plugins returns the stems whose register was called, in sorted order."
    assert app == {"commands": ["greet", "upper"]}, "Call each register with the same app dict, in sorted order."


def test_run_plugins_with_nothing(tmp_path):
    folder = write(tmp_path / "p", {"_private.py": REG.format(name="x")})
    app = {}
    assert run_plugins(folder, app) == [] and app == {}, "No public plugins: nothing is called."
