"""Tab completion. bash calls `learn _complete <cword> <words...>` and filters what we print."""

from __future__ import annotations

import argparse

from learn import content, paths
from learn.syllabus import load as load_syllabus


def _problem_ids() -> list[str]:
    return sorted(content.all_problems())


def _module_ids() -> list[str]:
    return [m.id for m in load_syllabus().modules()]


def _track_ids() -> list[str]:
    return list(load_syllabus().track_ids())


# Positional arguments whose values come from the content, by their argparse dest.
DYNAMIC = {
    "problem": _problem_ids,
    "module": _module_ids,
    "tracks": _track_ids,
    "track": _track_ids,
    "target": lambda: _module_ids() + _track_ids() + _problem_ids(),
}


def _subcommands(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def _values(action: argparse.Action) -> list[str]:
    if action.choices:
        return [str(c) for c in action.choices]
    if action.dest in DYNAMIC:
        return DYNAMIC[action.dest]()
    return []


def candidates(parser: argparse.ArgumentParser, words: list[str]) -> list[str]:
    """`words` are the words after `learn`, the last one being the word under the cursor."""
    subs = _subcommands(parser)
    if len(words) <= 1:
        return sorted(subs)
    sp = subs.get(words[0])
    if sp is None:
        return []
    cur = words[-1]
    by_flag = {o: a for a in sp._actions for o in a.option_strings}
    if cur.startswith("-"):
        return sorted(by_flag)
    prev = by_flag.get(words[-2])
    if prev is not None and prev.nargs != 0:
        return _values(prev) if prev.dest == "module" else [str(c) for c in prev.choices or []]
    positionals = [a for a in sp._actions if not a.option_strings]
    index, skip = 0, False
    for w in words[1:-1]:
        if skip:
            skip = False
        elif w in by_flag:
            skip = by_flag[w].nargs != 0
        elif not w.startswith("-"):
            index += 1
    if not positionals:
        return []
    action = positionals[min(index, len(positionals) - 1)]
    if index >= len(positionals) and action.nargs not in ("+", "*"):
        return []
    return _values(action)


def complete(parser: argparse.ArgumentParser, argv: list[str]) -> None:
    """argv is [cword, program, word1, word2, ...] exactly as bash passes them."""
    if not paths.syllabus_path().exists():
        return
    cword = int(argv[0])
    words = argv[2:cword + 2]
    if len(words) < cword:
        words.append("")
    try:
        print("\n".join(candidates(parser, words)))
    except Exception:  # completion must never print a traceback into the shell
        pass
