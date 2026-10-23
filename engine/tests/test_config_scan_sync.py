from learn import config, scan, sync


def test_config_set_keeps_comments_and_adds_keys(home):
    path = home / "config.toml"
    path.write_text("# my comment\n[plan]\ndaily_minutes = 60\n", encoding="utf-8")
    config.set_value("plan.daily_minutes", 120)
    config.set_value("accounts.codeforces_handle", "someone")
    text = path.read_text(encoding="utf-8")
    assert "# my comment" in text
    assert config.get("plan.daily_minutes") == 120
    assert config.get("accounts.codeforces_handle") == "someone"


def test_parse_cli_value():
    assert config.parse_cli_value("90") == 90
    assert config.parse_cli_value("true") is True
    assert config.parse_cli_value("core,dsa") == ["core", "dsa"]


def test_features_detected():
    src = (
        "import pandas as pd\n"
        "def deco(f):\n    def wrapper(*a):\n        return f(*a)\n    return wrapper\n"
        "@deco\nasync def go():\n    pass\n"
        "class A(Exception):\n    def __eq__(self, o):\n        return True\n"
        "x = [i for i in range(3)]\n"
    )
    f = scan.features_of(src)
    assert {"import:pandas", "closure", "decorator", "async", "class", "inheritance",
            "dunder-methods", "comprehension"} <= f
    assert {"da.03", "core.11", "core.21", "core.15"} <= scan.modules_of(f)


def test_leetcode_tree_dfs_maps_to_trees():
    mods = sync.modules_for_tags(["tree", "depth-first-search", "binary-tree"], sync.LC_TAG_MODULES)
    assert mods == ["dsa.10"]
    assert sync.modules_for_tags(["graph", "depth-first-search"], sync.LC_TAG_MODULES) == ["dsa.12"]


def test_snapshot_keeps_progress_out_of_the_course_repo(home):
    import shutil
    import subprocess

    import pytest
    from learn import gitsnap

    if not shutil.which("git"):
        pytest.skip("git not installed")
    work = home / "my-work" / "core" / "p001"
    (work / "__pycache__").mkdir(parents=True)
    (work / "solution.py").write_text("print('hi')\n", encoding="utf-8")
    (work / "__pycache__" / "solution.cpython-312.pyc").write_bytes(b"x")
    (home / "content" / "draft.md").write_text("half-written module\n", encoding="utf-8")

    assert gitsnap.snapshot("learn: solved p001"), "first snapshot should create the history and commit"
    files = subprocess.run(
        ["git", f"--git-dir={home / '.progress.git'}", "ls-files"], capture_output=True, text=True, encoding="utf-8"
    ).stdout.split()
    assert "my-work/core/p001/solution.py" in files
    assert "config.toml" in files
    assert not any("__pycache__" in f for f in files), "cache files must not be saved"
    assert not any(f.startswith("content/") for f in files), "course content must stay out of the private history"
    assert not (home / ".git").exists(), "the snapshot must never create or touch the course repo"
    assert not gitsnap.snapshot("again"), "nothing changed, so no new commit"

    (work / "solution.py").unlink()
    assert gitsnap.snapshot("deleted"), "a deleted solution is a change worth saving"
