import subprocess
import sys

import pytest

import solution
from solution import list_files, main


@pytest.fixture
def docs(tmp_path):
    for name in ("b.PDF", "a.txt", ".hidden", "c.txt"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "inner.txt").write_text("x", encoding="utf-8")
    return tmp_path


def test_list_files_skips_hidden_and_folders(docs):
    assert list_files(docs) == ["a.txt", "b.PDF", "c.txt"], \
        "Only regular files directly in the folder, sorted; no '.hidden', no 'sub', nothing from inside 'sub'."


def test_list_files_filters_by_extension_ignoring_case(docs):
    assert list_files(docs, ".pdf") == ["b.PDF"], "Compare suffixes in lower case: '.PDF' matches '.pdf'."
    assert list_files(docs, ".TXT") == ["a.txt", "c.txt"]


def test_data_goes_to_stdout_and_the_summary_to_stderr(docs, capsys):
    assert main([str(docs)]) == 0, "Success is exit code 0."
    out, err = capsys.readouterr()
    assert out.splitlines() == ["a.txt", "b.PDF", "c.txt"], \
        f"stdout must hold ONLY the file names (that is what '| wc -l' counts); got {out!r}"
    assert "3 file(s)" in err, f"The summary is a message for the human: print it to stderr. stderr was {err!r}"


def test_ext_option(docs, capsys):
    assert main([str(docs), "--ext", ".pdf"]) == 0
    assert capsys.readouterr().out.splitlines() == ["b.PDF"]


def test_empty_folder_is_still_success(tmp_path, capsys):
    assert main([str(tmp_path)]) == 0, "An empty folder is not an error: exit 0."
    out, err = capsys.readouterr()
    assert out == "" and "0 file(s)" in err


def test_missing_folder_is_exit_code_1(tmp_path, capsys):
    missing = tmp_path / "nope"
    assert main([str(missing)]) == 1, "A runtime failure (missing folder) is exit code 1."
    out, err = capsys.readouterr()
    assert out == "", "Nothing goes to stdout when there is no data."
    assert "is not a folder" in err and err.startswith("listfiles: error:"), f"Error format 'listfiles: error: ... is not a folder' on stderr; got {err!r}"


def test_a_file_is_not_a_folder(docs, capsys):
    assert main([str(docs / "a.txt")]) == 1, "A file given as the folder is a runtime failure too."


def test_usage_errors_are_exit_code_2(capsys):
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code == 2, "No folder is a usage error: let argparse exit with 2."
    with pytest.raises(SystemExit) as e:
        main(["x", "--colour"])
    assert e.value.code == 2, "An unknown option is a usage error too."


def test_as_a_real_program(docs):
    script = solution.__file__
    ok = subprocess.run([sys.executable, script, str(docs)], capture_output=True, text=True, timeout=30)
    assert ok.returncode == 0, f"The real program must exit 0; stderr: {ok.stderr}"
    assert len(ok.stdout.splitlines()) == 3, "As a program, stdout must still contain only the three names (what a pipe sees)."
    bad = subprocess.run([sys.executable, script, str(docs / "nope")], capture_output=True, text=True, timeout=30)
    assert bad.returncode == 1, "Keep 'sys.exit(main())' so the returned 1 becomes the process exit code."
    usage = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=30)
    assert usage.returncode == 2, "A usage error is exit code 2 for the real program."
