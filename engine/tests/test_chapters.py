"""Tests for the chapter tools: parsing, lint, running code blocks, extracting files, flashcards, doctor."""
import ast
import sys
import textwrap
from pathlib import Path

import pytest

from learn import chapters as C
from learn import cli, doctor

ROOT = Path(__file__).resolve().parents[2]
ALL_CHAPTERS = sorted((ROOT / "content").glob("*/*/chapter.md"))


def md(body: str) -> str:
    return textwrap.dedent(body).lstrip("\n")


GOOD = md('''
    # Title

    Intro.

    ## 1. One

    Text.

    ## 2. Two

    ```python run
    print("hi")
    ```
    ```text
    hi
    ```

    ## 3. Three

    > **Visualise it** *(optional)*
    > "Draw a thing."

    After the box.

    1. Q one is long enough?

    <details><summary>Answer</summary>

    1. Yes it is.

    </details>
''')


def rules(text):
    return [(i.level, i.rule) for i in C.lint_chapter(text)]


# ---------------------------------------------------------------- parsing

def test_parse_blocks_finds_info_code_and_lines():
    blocks, unclosed = C.parse_blocks(GOOD)
    assert unclosed == 0 and [b.info for b in blocks] == ["python run", "text"]
    assert blocks[0].code == 'print("hi")' and blocks[0].is_python_run and not blocks[1].is_python_run


def test_unclosed_fence_is_reported_with_its_line():
    blocks, unclosed = C.parse_blocks("# T\n\n```python\nx = 1\n")
    assert unclosed == 3


def test_fences_in_blockquotes_and_longer_fences_are_handled():
    text = "> ```bash\n> ls\n> ```\n\n````text\n```\ninside\n```\n````\n"
    blocks, unclosed = C.parse_blocks(text)
    assert unclosed == 0 and len(blocks) == 1 and "inside" in blocks[0].code, "a 4-backtick fence may contain 3-backtick lines; a blockquote fence is not a fence"


# ---------------------------------------------------------------- lint

def test_a_good_chapter_has_no_errors():
    assert [r for r in rules(GOOD) if r[0] == "error"] == []


def test_lint_catches_each_structural_mistake():
    assert ("error", "fence") in rules("# T\n\n## A\n\n```python\nx\n")
    assert ("error", "inline-fence") in rules(GOOD.replace("Text.", "Text ```python run here"))
    assert ("error", "empty-output") in rules(GOOD.replace("```text\nhi\n```", "```text\n```"))
    assert ("error", "syntax") in rules(GOOD.replace('print("hi")', "print("))
    assert ("error", "details") in rules(GOOD.replace("</details>", ""))
    assert ("error", "details") in rules(GOOD.replace("<details><summary>", "> <details><summary>"))
    assert ("error", "details") in rules(GOOD.replace("Yes it is.\n\n</details>", "Yes it is. </details>"))
    assert ("error", "visualise") in rules(GOOD.replace('> "Draw a thing."\n\nAfter', '> "Draw a thing."\nAfter'))
    assert ("error", "title") in rules(GOOD.replace("# Title\n", ""))
    assert ("error", "sections") in rules("# T\n\n## A\n\ntext\n")


def test_hash_signs_inside_code_blocks_are_not_headings():
    text = GOOD.replace('print("hi")', '# a comment\n## looks like a heading\nprint("hi")')
    assert [r for r in rules(text) if r[0] == "error"] == []


def test_empty_output_is_allowed_after_shell_commands():
    text = GOOD.replace("```python run\nprint(\"hi\")\n```\n```text\nhi\n```", "```bash run\nmkdir x\n```\n```text\n```")
    assert ("error", "empty-output") not in rules(text)


def test_every_real_chapter_passes_lint():
    bad = {}
    for path in ALL_CHAPTERS:
        errors = [str(i) for i in C.lint_chapter(path.read_text(encoding="utf-8")) if i.level == "error"]
        if errors:
            bad[path.parent.name] = errors[:3]
    assert len(ALL_CHAPTERS) == 92 and not bad, f"chapters with lint errors: {bad}"


# ---------------------------------------------------------------- Windows text encoding

def test_encoding_issues_found_in_text_calls_but_not_binary():
    code = 'from pathlib import Path\nPath("a").write_text("x")\nPath("a").read_text()\nopen("f")\nopen("f", "w")\nopen("f", "rb")\nopen("f", encoding="utf-8")\nPath("a").write_text("x", encoding="utf-8")\n'
    assert [ln for ln, _ in C.encoding_issues(code)] == [2, 3, 4, 5]


def test_encoding_issue_inside_a_file_written_by_the_code():
    code = 'import pathlib\n(pathlib.Path("m.py")).write_text(r\'\'\'import pathlib\nx = pathlib.Path("t").read_text()\n\'\'\', encoding="utf-8")\n'
    found = C.encoding_issues(code)
    assert len(found) == 1 and "inside the file written at line 2" in found[0][1]


def test_fix_encoding_adds_the_argument_and_is_safe():
    code = 'p.write_text("x")\ns = p.read_text()\nwith open("f") as fh:\n    fh.read()\nopen("b", "rb")\n'
    fixed = C.fix_encoding(code)
    assert fixed == 'p.write_text("x", encoding="utf-8")\ns = p.read_text(encoding="utf-8")\nwith open("f", encoding="utf-8") as fh:\n    fh.read()\nopen("b", "rb")\n'
    assert C.fix_encoding(fixed) == fixed, "running it twice changes nothing"
    ast.parse(fixed)


def test_fix_encoding_reaches_into_raw_triple_quoted_files_and_keeps_non_ascii():
    code = 'import pathlib\n(pathlib.Path("m.py")).write_text(r\'\'\'import pathlib\ntext = pathlib.Path("t").read_text()  # café\n\'\'\')\n'
    fixed = C.fix_encoding(code)
    ast.parse(fixed)
    assert fixed.count('encoding="utf-8"') == 2 and "café" in fixed
    assert C.encoding_issues(fixed) == []


def test_fix_chapter_encoding_changes_only_python_blocks():
    text = md('''
        # T

        ## A

        ```python run
        open("f")
        ```
        ```text
        open("f")
        ```

        ## B
        ## C
    ''')
    new, n = C.fix_chapter_encoding(text)
    assert n == 1 and new.count('open("f", encoding="utf-8")') == 1 and new.count('open("f")') == 1


# ---------------------------------------------------------------- run the code blocks

def test_verify_runs_blocks_in_order_in_one_namespace():
    r = C.verify_chapter(md('''
        # T

        ```python run
        x = 2
        print(x)
        ```
        ```text
        2
        ```

        ```python run
        print(x * 3)
        ```
        ```text
        6
        ```
    '''), diff=True)
    assert r.blocks == 2 and r.ran == 2 and not r.failed and r.same_output == 2


def test_verify_reports_the_failing_block_and_its_line():
    r = C.verify_chapter("# T\n\n```python run\nprint(1)\n```\n\n```python run\nraise ValueError('boom')\n```\n")
    assert r.ran == 1 and len(r.failed) == 1 and r.failed[0][0] == 7 and "ValueError: boom" in r.failed[0][1]


def test_verify_diff_notices_a_different_output():
    r = C.verify_chapter("# T\n\n```python run\nprint('a')\n```\n```text\nb\n```\n", diff=True)
    assert r.same_output == 0 and r.different_output == [3]


def test_strict_encoding_mode_catches_text_files_opened_without_an_encoding():
    bad = "# T\n\n```python run\nopen('x.txt', 'w').write('hi')\n```\n"
    good = "# T\n\n```python run\nopen('x.txt', 'w', encoding='utf-8').write('hi')\n```\n"
    assert C.verify_chapter(bad, strict_encoding=True).failed, "this is the Windows bug: the default encoding is not UTF-8"
    assert not C.verify_chapter(good, strict_encoding=True).failed


# ---------------------------------------------------------------- extract

PROJECT = md('''
    # T

    ```python run
    import pathlib
    pkg = pathlib.Path("pkg")
    (pkg / "mod.py").write_text(r\'\'\'def f():
        return 1
    \'\'\', encoding="utf-8")
    (pkg / "sub" / "deep.txt").write_text("deep", encoding="utf-8")
    (pkg / name).write_text("not a literal path", encoding="utf-8")
    ```
''')


def test_extract_finds_literal_files_only():
    files = C.extract_files(PROJECT)
    assert [(f.root, f.relpath) for f in files] == [("pkg", "mod.py"), ("pkg", "sub/deep.txt")]
    assert files[0].content == "def f():\n    return 1\n"


def test_write_extracted_respects_existing_files_and_never_escapes(tmp_path):
    files = C.extract_files(PROJECT) + [C.ExtractedFile("pkg", "../evil.py", "x = 1")]
    written, skipped = C.write_extracted(files, tmp_path)
    assert sorted(p.name for p in written) == ["deep.txt", "mod.py"] and not (tmp_path / "evil.py").exists() and not (tmp_path.parent / "evil.py").exists()
    written2, skipped2 = C.write_extracted(C.extract_files(PROJECT), tmp_path)
    assert written2 == [] and len(skipped2) == 2
    assert len(C.write_extracted(C.extract_files(PROJECT), tmp_path, force=True)[0]) == 2


def test_the_llm_chapters_extract_runnable_projects(tmp_path):
    for module, minimum in (("llm.02", 10), ("llm.05", 10), ("llm.07", 12)):
        chapter = next((ROOT / "content" / "llm").glob(f"{module}-*/chapter.md"))
        files = C.extract_files(chapter.read_text(encoding="utf-8"))
        assert len(files) >= minimum, f"{module}: expected the project's files to be extractable"
        for f in files:
            if f.relpath.endswith(".py"):
                ast.parse(f.content)


# ---------------------------------------------------------------- flashcards

def test_cards_pair_questions_with_answers_by_number():
    text = md('''
        # T

        ## 1. S

        ### 1.4 Try it

        1. What does the model actually do when it uses a tool?
        2. Why does each message carry an id?

        <details><summary>Answer</summary>

        1. It writes a structured request.
        2. To match results to calls.

        </details>
    ''')
    cards = C.make_cards(text)
    assert [(c.front, c.back) for c in cards] == [("What does the model actually do when it uses a tool?", "It writes a structured request."),
                                                  ("Why does each message carry an id?", "To match results to calls.")]
    assert cards[0].section == "1.4 Try it"


def test_cards_ignore_blockquotes_and_short_items():
    text = "## A\n\n> 1. quoted\n\n1. ok?\n\n<details><summary>Answer</summary>\n\n1. a\n\n</details>\n"
    assert C.make_cards(text) == []


def test_real_chapters_make_many_cards():
    total = sum(len(C.make_cards(p.read_text(encoding="utf-8"))) for p in ALL_CHAPTERS)
    assert total > 1000, f"expected hundreds of flashcards from the question-and-answer boxes, got {total}"


# ---------------------------------------------------------------- doctor

def test_requirements_group_the_packages():
    req = doctor.load_requirements()
    assert req.group_of("numpy") == "base" and req.group_of("torch") == "ml" and req.group_of("pypdf") == "llm" and req.group_of("anthropic") == "providers"
    assert req.group_of("scikit_learn") == "base" and req.group_of("not-a-package") is None


def test_imports_of_marks_try_except_imports_as_optional():
    code = "import os\nimport numpy as np\ntry:\n    import torch\nexcept ImportError:\n    torch = None\nfrom pandas import DataFrame\nfrom . import local\n"
    assert sorted(doctor.imports_of(code)) == [("numpy", False), ("os", False), ("pandas", False), ("torch", True)]


def test_chapter_needs_separates_installed_missing_local_and_undeclared():
    req = doctor.Requirements(base={"numpy": "numpy"}, extras={"ml": {"torch": "torch>=2"}})
    text = md('''
        # T

        ```python run
        import os, numpy, mylocal, mystery, torch
        import pathlib
        pathlib.Path("mylocal.py").write_text("x = 1", encoding="utf-8")
        ```
    ''')
    needs = doctor.chapter_needs(text, req)
    assert "numpy" in needs.installed and "mylocal" not in needs.undeclared, "a module the chapter writes itself is not a dependency"
    assert needs.undeclared == ["mystery"]
    if doctor.importlib.util.find_spec("torch") is None:
        assert needs.missing == {"torch": "ml"}


def test_every_package_the_chapters_import_is_declared_in_pyproject():
    req = doctor.load_requirements()
    undeclared = {}
    for p in ALL_CHAPTERS:
        n = doctor.chapter_needs(p.read_text(encoding="utf-8"), req)
        if n.undeclared:
            undeclared[p.parent.name] = n.undeclared
    assert not undeclared, f"imports not listed in pyproject.toml: {undeclared}"


def test_environment_report_has_the_essentials():
    labels = [r[0] for r in doctor.environment_report()]
    assert {"Python", "UTF-8 mode", "git"} <= set(labels)


# ---------------------------------------------------------------- the commands

def test_lint_command_exit_status(tmp_path, monkeypatch, capsys):
    from learn import syllabus
    monkeypatch.setenv("LEARN_HOME", str(ROOT))
    syllabus.load.cache_clear()
    assert cli.main(["lint", "llm.01"]) == 0
    assert "0 errors" in capsys.readouterr().out


def test_doctor_and_capstone_commands_run(monkeypatch, capsys):
    from learn import syllabus
    monkeypatch.setenv("LEARN_HOME", str(ROOT))
    syllabus.load.cache_clear()
    assert cli.main(["doctor", "llm.03"]) == 0
    assert "What the chapters import" in capsys.readouterr().out
    assert cli.main(["capstone"]) == 0
    out = capsys.readouterr().out
    assert all(f"learn capstone {t}" in out for t in ("core", "dsa", "swe", "da", "ds", "ml", "llm"))
    assert cli.main(["capstone", "llm", "--print"]) == 0
    assert "LLM capstone" in capsys.readouterr().out


def test_cards_and_extract_commands_write_files(tmp_path, monkeypatch, capsys):
    from learn import syllabus
    monkeypatch.setenv("LEARN_HOME", str(ROOT))
    syllabus.load.cache_clear()
    out = tmp_path / "cards.csv"
    assert cli.main(["cards", "llm.05", "--out", str(out)]) == 0
    first = out.read_text(encoding="utf-8").splitlines()
    assert first[0] == "front,back,module,section" and len(first) > 10
    anki = tmp_path / "cards.tsv"
    assert cli.main(["cards", "llm.05", "--anki", "--out", str(anki)]) == 0 and "\t" in anki.read_text(encoding="utf-8")
    assert cli.main(["extract", "llm.05", "--out", str(tmp_path / "proj")]) == 0
    assert (tmp_path / "proj" / "pkg" / "agent.py").exists() and (tmp_path / "proj" / "pkg" / "test_agent.py").exists()
    assert cli.main(["extract", "core.01", "--out", str(tmp_path / "none")]) == 0
    assert "nothing to extract" in capsys.readouterr().out


def test_extracted_llm_project_passes_its_own_tests(tmp_path, monkeypatch):
    """The extracted files are a working project: this is the point of the command."""
    import subprocess
    from learn import syllabus
    monkeypatch.setenv("LEARN_HOME", str(ROOT))
    syllabus.load.cache_clear()
    assert cli.main(["extract", "llm.04", "--out", str(tmp_path)]) == 0
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=tmp_path / "pkg", capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout[-800:]
