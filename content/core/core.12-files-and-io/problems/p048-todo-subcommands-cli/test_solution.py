import json

import pytest

from solution import main


def run(tmp_path, capsys, *args):
    code = main(["--file", str(tmp_path / "t.json"), *args])
    shown = capsys.readouterr()
    return code, shown.out, shown.err


def test_add_and_list(tmp_path, capsys):
    assert run(tmp_path, capsys, "add", "buy milk", "--priority", "high") == (0, "added 1\n", ""), "add prints 'added <id>' and returns 0."
    assert run(tmp_path, capsys, "add", "call Ana") == (0, "added 2\n", ""), "The next id is the highest id + 1."
    code, out, _ = run(tmp_path, capsys, "list")
    assert (code, out) == (0, "1 [ ] buy milk (high)\n2 [ ] call Ana (normal)\n"), "list shows '<id> [ ] <text> (<priority>)'. The default priority is normal."


def test_file_format(tmp_path, capsys):
    run(tmp_path, capsys, "add", "x", "--priority", "low")
    data = json.loads((tmp_path / "t.json").read_text(encoding="utf-8"))
    assert data == [{"id": 1, "text": "x", "done": False, "priority": "low"}], "Save a JSON list of dicts with the keys id, text, done, priority."


def test_done_and_filters(tmp_path, capsys):
    for text in ["a", "b", "c"]:
        run(tmp_path, capsys, "add", text)
    assert run(tmp_path, capsys, "done", "2") == (0, "done 2\n", ""), "done prints 'done <id>'."
    assert run(tmp_path, capsys, "list")[1] == "1 [ ] a (normal)\n3 [ ] c (normal)\n", "Plain list hides done todos."
    assert run(tmp_path, capsys, "list", "--done")[1] == "2 [x] b (normal)\n", "--done shows only done todos, with [x]."
    assert run(tmp_path, capsys, "list", "--all")[1] == "1 [ ] a (normal)\n2 [x] b (normal)\n3 [ ] c (normal)\n", "--all shows everything, sorted by id."


def test_nothing_to_do(tmp_path, capsys):
    assert run(tmp_path, capsys, "list") == (0, "nothing to do\n", ""), "An empty list prints 'nothing to do' and returns 0."
    run(tmp_path, capsys, "add", "a")
    run(tmp_path, capsys, "done", "1")
    assert run(tmp_path, capsys, "list")[1] == "nothing to do\n", "If every todo is done, the plain list is empty too."


def test_remove_and_id_not_reused(tmp_path, capsys):
    for text in ["a", "b", "c"]:
        run(tmp_path, capsys, "add", text)
    assert run(tmp_path, capsys, "remove", "3") == (0, "removed 3\n", ""), "remove prints 'removed <id>'."
    assert run(tmp_path, capsys, "remove", "1")[0] == 0, "Removing the first todo is fine."
    assert run(tmp_path, capsys, "add", "d")[1] == "added 3\n", "New id is the highest id + 1: the list is [2], so the new id is 3."


def test_new_id_after_removing_a_middle_one(tmp_path, capsys):
    for text in ["a", "b", "c"]:
        run(tmp_path, capsys, "add", text)
    run(tmp_path, capsys, "remove", "2")
    assert run(tmp_path, capsys, "add", "d")[1] == "added 4\n", "Do not use len(todos)+1: that would give 3, which already exists."


@pytest.mark.parametrize("command", ["done", "remove"])
def test_unknown_id(tmp_path, capsys, command):
    run(tmp_path, capsys, "add", "a")
    before = (tmp_path / "t.json").read_text(encoding="utf-8")
    code, out, err = run(tmp_path, capsys, command, "9")
    assert code == 1, "An unknown id gives exit code 1."
    assert out == "" and err == "no such id: 9\n", "Print 'no such id: 9' to stderr only."
    assert (tmp_path / "t.json").read_text(encoding="utf-8") == before, "The file must not change."


def test_list_does_not_create_file(tmp_path, capsys):
    run(tmp_path, capsys, "list")
    assert not (tmp_path / "t.json").exists(), "A read-only command must not create or write the file."


@pytest.mark.parametrize("bad", [
    ["add", "x", "--priority", "urgent"],
    ["list", "--all", "--done"],
    ["done", "abc"],
    ["remove"],
    [],
    ["fly"],
])
def test_bad_usage_exits_2(tmp_path, bad):
    with pytest.raises(SystemExit) as info:
        main(["--file", str(tmp_path / "t.json"), *bad])
    assert info.value.code == 2, f"The arguments {bad} are wrong. argparse exits with code 2: use choices, type=int, a mutually exclusive group, and required=True on the subparsers."


def test_file_option_is_required(tmp_path):
    with pytest.raises(SystemExit) as info:
        main(["list"])
    assert info.value.code == 2, "--file is required (required=True)."
