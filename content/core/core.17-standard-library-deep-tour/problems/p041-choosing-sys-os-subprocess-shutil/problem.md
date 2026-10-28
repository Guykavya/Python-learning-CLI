# Explain: sys, os, subprocess or shutil?

Four standard modules talk to "the system", and beginners mix them up:

- `sys` is about **the Python interpreter itself**: its arguments, its streams, its exit code, its path.
- `os` is about **the operating system** at a low level: environment variables, single files and folders, process ids.
- `shutil` is **high-level file work** built on `os`: whole trees, copies with metadata, archives, finding programs.
- `subprocess` **starts other programs** and talks to them.

For each task below, name the module **and** the function (or attribute) you would use, and give
one sentence of *why*: what would go wrong, or be harder, with the obvious alternative.

1. Launch a helper Python script with **the same Python** that is running your program (inside a virtual environment).
2. Read the environment variable `BACKUP_DIR`, falling back to `"backups"` if it is not set.
3. Copy a whole folder, with sub-folders, to a new place.
4. Delete a folder that still has files in it.
5. Check whether the program `git` is installed, before trying to run it.
6. Run `git status --short` and get its output as a string.
7. Stop the program with exit code `2` after printing an error message where error messages belong.
8. A classmate writes `os.system("cp -r " + src + " " + dst)`. Give **three** reasons this is a bad idea.

Write your answer in `answer.md` (about 250 to 400 words). Short bullet points are fine.

**Example of the expected style**

> **0. Know which operating system you are on.** `sys.platform` (`"linux"`, `"win32"`, `"darwin"`).
> It is a fixed string about the interpreter's build; `os.name` gives only `"posix"` or `"nt"`, which is too coarse to tell Linux from macOS.
