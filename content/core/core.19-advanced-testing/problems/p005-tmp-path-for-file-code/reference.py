from target import load_notes, save_notes


def test_round_trip(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["buy milk", "call Ana"])
    assert load_notes(path) == ["buy milk", "call Ana"], "What you save must load back unchanged."


def test_file_has_one_note_per_line_with_final_newline(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["a", "b"])
    assert path.read_text(encoding="utf-8") == "a\nb\n", "Every note, including the last, ends with a newline."


def test_saving_again_replaces_the_file(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["old", "older"])
    save_notes(path, ["new"])
    assert load_notes(path) == ["new"], "A second save must replace the old content, not append to it."


def test_missing_file_gives_empty_list(tmp_path):
    assert load_notes(tmp_path / "nope.txt") == [], "A file that does not exist means no notes."


def test_blank_lines_are_skipped(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("a\n\n   \nb\n", encoding="utf-8")
    assert load_notes(path) == ["a", "b"], "Blank and whitespace-only lines are not notes."


def test_notes_come_back_without_newlines(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["x", "y", "z"])
    assert load_notes(path) == ["x", "y", "z"], "No newline characters in the loaded notes; all three notes present."


def test_leading_spaces_are_kept(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["  indented"])
    assert load_notes(path) == ["  indented"], "Only blank lines are dropped; spaces inside a note stay."


def test_empty_list_gives_empty_file(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, [])
    assert path.read_text(encoding="utf-8") == "", "No notes means an empty file."
    assert load_notes(path) == []
