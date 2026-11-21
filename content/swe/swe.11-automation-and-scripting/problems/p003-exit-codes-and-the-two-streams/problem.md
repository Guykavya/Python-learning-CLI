# Exit codes and the two streams

Chapter sections 2.2 (the skeleton), 2.3 (exit codes are the script's real answer) and 2.4 (stdout, stderr and the pipe). A tool talks to the world through three channels: **stdout** for its data, **stderr** for messages to the human, and the **exit code** for the verdict. Mixing them breaks pipes (`listfiles docs | wc -l` must count files, not messages) and lies to cron.

## What to write

A small tool `listfiles FOLDER [--ext EXT]`:

```python
def list_files(folder, ext=None) -> list[str]: ...
def build_parser() -> argparse.ArgumentParser: ...
def main(argv=None) -> int: ...
```

- `list_files` returns the **names** of the regular files directly inside `folder` (no subfolders, no hidden files whose name starts with `.`), sorted. With `ext` (such as `".txt"` or `".TXT"`), only files whose suffix matches, ignoring case.
- `build_parser()` uses `prog="listfiles"`, a positional `folder` (`type=Path`) and an option `--ext`.
- `main(argv)`:
  - prints each file name on its own line to **stdout** (data only, nothing else on stdout);
  - prints `N file(s)` to **stderr** at the end;
  - returns **0** on success, even when the folder is empty;
  - if the folder does not exist or is not a folder: prints `listfiles: error: <folder> is not a folder` to **stderr**, prints nothing to stdout, returns **1**;
  - a usage error (no folder given, unknown option) is left to argparse, which exits with code **2** by raising `SystemExit(2)`.
- Keep the `if __name__ == "__main__": sys.exit(main())` block of the starter: the tests also run your file as a real program and look at its exit code.

## Example

```text
$ python solution.py docs
a.txt
b.PDF
2 file(s)                      <- this line is on stderr
$ python solution.py docs | wc -l
2
$ python solution.py nope; echo $?
listfiles: error: nope is not a folder
1
$ python solution.py; echo $?
usage: listfiles [-h] [--ext EXT] folder
listfiles: error: the following arguments are required: folder
2
```
