# Project: a file organiser CLI

Build a small command-line tool that sorts the files of a messy folder (like `Downloads`) into sub-folders.
It must be **safe**: it never overwrites a file, it can show what it would do without doing it, and running it
twice is harmless. This project uses `argparse`, `pathlib`, `shutil`, error handling and exit codes.

Write `main(argv=None)` in `solution.py`. It returns an exit code. It never calls `sys.exit` by itself
(argparse may raise `SystemExit` for bad usage).

## Arguments

```text
organiser SOURCE [--by {type,date,size}] [--dest DEST] [--dry-run]
```

- `SOURCE`: the folder with the messy files. Required.
- `--by`: how to sort. `type` (default), `date` or `size`.
- `--dest`: the folder that receives the sub-folders. Default: `SOURCE` itself. It is created when needed.
- `--dry-run`: print what would happen, change nothing on disk.

## Which files

Only the **files directly inside `SOURCE`**, in the order of their names (plain string sort). Leave alone:
hidden files (the name starts with `.`) and every sub-folder with its content.

## Sub-folder names

| `--by` | Folder | Rule |
|---|---|---|
| `type` | `images` | `.jpg .jpeg .png .gif` |
| | `documents` | `.pdf .doc .docx .txt .md` |
| | `data` | `.csv .json .xml .toml` |
| | `code` | `.py .js .html .css` |
| | `archives` | `.zip .tar .gz` |
| | `other` | everything else, also files without an extension |
| `date` | `YYYY-MM` | the month of the modification time (`st_mtime`, local time) |
| `size` | `small` | under 1024 bytes |
| | `medium` | 1024 bytes up to 102399 bytes |
| | `large` | 102400 bytes or more |

Extensions are compared in lower case (`photo.JPG` is an image).

## Never overwrite

If the target name already exists in the target folder, use a numeric suffix before the extension:
`notes.txt` becomes `notes_1.txt`, then `notes_2.txt` and so on. The existing file is never touched.
Names that you have already **planned** in the same run count as taken, so a dry run shows exactly what a real run does.
Move files with `shutil.move`.

## Output

- For each file, one line: `moved NAME -> FOLDER/NEWNAME` (the target path relative to `DEST`, with `/`).
  With `--dry-run` the line starts with `would move` instead of `moved`.
- Last line, the summary: `moved 7 files` or `would move 7 files` (`1 file` when it is exactly one).
- If there is nothing to move: print `nothing to do`, return `0`, and create nothing.

## Exit codes

| Code | When |
|---|---|
| `0` | everything went well (also "nothing to do") |
| `1` | a move failed with `OSError`: print `error: cannot move NAME: ...` to **stderr**, go on with the other files, and return `1` at the end. The summary counts only the moved files |
| `2` | `SOURCE` is not a folder, or `DEST` exists and is not a folder: print `error: ...` to **stderr**, nothing to stdout, nothing changed. Bad arguments (`--by colour`, no source): argparse exits with 2 |

## Idempotent

A second run on the same folder finds no files in the top level of `SOURCE`, prints `nothing to do`, and changes nothing.

## Example

```text
$ organiser ~/Downloads --dry-run
would move README -> other/README
would move notes.txt -> documents/notes.txt
would move photo.JPG -> images/photo.JPG
would move 3 files
$ organiser ~/Downloads
moved README -> other/README
moved notes.txt -> documents/notes.txt
moved photo.JPG -> images/photo.JPG
moved 3 files
$ organiser ~/Downloads
nothing to do
```
