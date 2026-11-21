# Twice is harmless, undo is exact

Chapter sections 3 (`undo` and `main` of `tidy.py`), 4 (testing a command-line tool) and "Try it: the test that proves it". A tool you can run on a real folder without fear gives three guarantees: the **dry run** changes nothing, a **second run** is harmless, and **undo** puts everything back exactly.

## What to write

The starter gives the tidy library from p005 and p006 (`category_for`, `unique_destination`, `plan_moves`, `apply_moves`, `JOURNAL`) and `build_parser()` with two subcommands, `organize FOLDER [-n/--dry-run]` and `undo FOLDER`. Write:

```python
def undo(root) -> list[tuple[Path, Path]]: ...
def main(argv=None) -> int: ...
```

`undo(root)`:
- if there is no journal, returns `[]` and changes nothing;
- reads the journal and walks it **in reverse order**; for each `[src, dst]`, if `dst` still exists and `src` is free, moves `dst` back to `src` (never overwrite a file that has appeared at `src` since);
- after each move back, removes the category folder **if it is now empty** (leave it if anything else is inside);
- deletes the journal and returns the list of `(dst, src)` pairs it restored.

`main(argv)`:
- if `folder` is not a folder: prints `tidy: error: <folder> is not a folder` to stderr, returns `1`;
- `organize`: plans and applies; prints one line per move to **stdout**: `moved: a.pdf -> documents/a.pdf` (or `would move: ...` in a dry run). Print the destination relative to the folder with forward slashes (`dst.relative_to(folder).as_posix()`), so the output is the same on Windows. Then prints `N file(s) moved` (or `N file(s) to move` in a dry run) to **stderr**;
- `undo`: prints `restored N file(s)` to stdout;
- returns `0`.

## Example

```text
$ python solution.py organize mess --dry-run
would move: a.pdf -> documents/a.pdf
would move: b.PNG -> images/b.PNG
2 file(s) to move                    (stderr)
$ python solution.py organize mess
moved: a.pdf -> documents/a.pdf
moved: b.PNG -> images/b.PNG
2 file(s) moved                      (stderr)
$ python solution.py organize mess
0 file(s) moved                      (stderr: run two is harmless)
$ python solution.py undo mess
restored 2 file(s)
```
