# shlex: split and join command lines

`'cp "my notes.txt" backup/'.split()` gives `['cp', '"my', 'notes.txt"', 'backup/']`: the quotes
are not understood. The `shlex` module splits and quotes text using the rules of a POSIX shell
(the shell of Linux and macOS), without running any shell:

- `shlex.split(line, comments=True)` respects `'...'` and `"..."` and drops an unquoted `# comment`.
- `shlex.join(args)` builds one line from a list, quoting each argument that needs it, so that
  `shlex.split(shlex.join(args)) == args`. (`shlex.quote(arg)` quotes a single argument.)

These are pure string functions and behave the same on Windows. (They follow POSIX rules; the
Windows command line has different quoting rules, which is one more reason to pass arguments to
`subprocess` as a list, as the next problems do.)

Write in `solution.py`:

1. `split_command(line) -> list[str]`: split like a shell, with comments. An unclosed quote raises
   `ValueError` (shlex already does).
2. `join_command(args) -> str`: the inverse of `split_command`.
3. `parse_settings(line) -> dict[str, str]`: a line of `key=value` settings, split like a
   shell (quotes and comments allowed). Split each token at the **first** `=`. A token without
   `=` or with an empty key raises `ValueError`. A later duplicate key wins.

**Examples**

```python
split_command('cp "my notes.txt" backup/   # copy it')   # ['cp', 'my notes.txt', 'backup/']
join_command(["cp", "my notes.txt", "backup/"])          # "cp 'my notes.txt' backup/"
join_command(["rm", "x; rm -rf ~"])                      # "rm 'x; rm -rf ~'"
parse_settings('name="Kavya B" city=Delhi url=a=b')      # {'name': 'Kavya B', 'city': 'Delhi', 'url': 'a=b'}
```
