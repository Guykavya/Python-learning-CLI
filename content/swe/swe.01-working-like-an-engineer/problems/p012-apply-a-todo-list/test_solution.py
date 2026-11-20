import pytest

from solution import apply_todo, autosquash

COMMITS = [("a1", "Add login"), ("b2", "Add search"), ("c3", "fixup! Add login"), ("d4", "Add docs")]


def test_apply_pick_reword_drop():
    todo = [("pick", "a1"), ("reword", "b2", "Add full-text search"), ("pick", "c3"), ("drop", "d4")]
    assert apply_todo(COMMITS, todo) == ["Add login", "Add full-text search", "fixup! Add login"]


def test_fixup_and_squash_meld_into_the_previous_commit():
    todo = [("pick", "a1"), ("fixup", "c3"), ("pick", "b2"), ("squash", "d4")]
    assert apply_todo(COMMITS, todo) == ["Add login", "Add search"], (
        "fixup and squash add no commit: they meld into the one above; its subject stays.")


def test_reorder_follows_the_todo():
    todo = [("pick", "d4"), ("pick", "b2"), ("pick", "a1")]
    assert apply_todo(COMMITS, todo) == ["Add docs", "Add search", "Add login"], "The todo list decides the order."


def test_commits_missing_from_the_todo_are_lost():
    assert apply_todo(COMMITS, [("pick", "a1")]) == ["Add login"], "A commit with no line in the todo is lost."


def test_squash_into_a_reworded_commit_keeps_the_new_subject():
    todo = [("reword", "a1", "Login page"), ("squash", "c3")]
    assert apply_todo(COMMITS, todo) == ["Login page"]


def test_squash_first_is_an_error():
    with pytest.raises(ValueError):
        apply_todo(COMMITS, [("squash", "a1"), ("pick", "b2")])
    with pytest.raises(ValueError):
        apply_todo(COMMITS, [("drop", "a1"), ("fixup", "b2")])  # nothing left to meld into


def test_unknown_command_or_sha():
    with pytest.raises(ValueError):
        apply_todo(COMMITS, [("edit", "a1")])
    with pytest.raises(ValueError):
        apply_todo(COMMITS, [("pick", "zzz")])


def test_autosquash_moves_the_fixup_after_its_target():
    assert autosquash(COMMITS) == [("pick", "a1"), ("fixup", "c3"), ("pick", "b2"), ("pick", "d4")]


def test_autosquash_several_and_squash_and_no_target():
    commits = [("a1", "Add login"), ("b2", "Add search"), ("c3", "fixup! Add login"), ("d4", "Add docs"),
               ("e5", "squash! Add search"), ("f6", "fixup! Add login"), ("g7", "fixup! Missing thing")]
    assert autosquash(commits) == [
        ("pick", "a1"), ("fixup", "c3"), ("fixup", "f6"),
        ("pick", "b2"), ("squash", "e5"),
        ("pick", "d4"), ("pick", "g7")], (
        "Each fixup goes right after its target, several fixups keep their order, and one without a target stays a pick.")


def test_autosquash_without_fixups_is_all_pick():
    assert autosquash([("a", "One"), ("b", "Two")]) == [("pick", "a"), ("pick", "b")]
    assert autosquash([]) == []


def test_autosquash_then_apply():
    todo = autosquash(COMMITS)
    assert apply_todo(COMMITS, todo) == ["Add login", "Add search", "Add docs"]
