# A todo tool with subcommands

Tools like `git add` and `git commit` have **subcommands**. `argparse` supports them with `add_subparsers`.
Write `main(argv=None)` in `solution.py` for a todo tool. It returns an exit code and never calls `sys.exit` itself
(argparse may raise `SystemExit` for bad usage, which is fine).

**Global option:** `--file PATH` is **required** and comes before the subcommand. The todos are saved there as a JSON list
of dicts `{"id": 1, "text": "...", "done": false, "priority": "normal"}`. A missing file means an empty list.

**Subcommands** (a subcommand is required)

| Command | What it does | Output | Exit code |
|---|---|---|---|
| `add TEXT [--priority P]` | `P` is one of `low`, `normal` (default), `high`. New id = highest id + 1 (1 when the list is empty). | `added <id>` | 0 |
| `list [--all \| --done]` | Without options: show todos that are not done. `--all`: all todos. `--done`: only done todos. The two options cannot be used together. | one line per todo, sorted by id: `<id> [ ] <text> (<priority>)`, or `[x]` for done. If there is nothing to show: `nothing to do` | 0 |
| `done ID` | Mark todo `ID` as done. `ID` is an `int`. | `done <id>` | 0 |
| `remove ID` | Delete todo `ID`. | `removed <id>` | 0 |

If `ID` does not exist, `done` and `remove` print `no such id: <id>` to **stderr**, change nothing, and return `1`.
Bad usage (unknown priority, `--all` with `--done`, `done abc`, no subcommand, no `--file`) makes argparse exit with code 2.

**Example**

```text
$ todo --file t.json add "buy milk" --priority high
added 1
$ todo --file t.json add "call Ana"
added 2
$ todo --file t.json done 1
done 1
$ todo --file t.json list
2 [ ] call Ana (normal)
$ todo --file t.json list --all
1 [x] buy milk (high)
2 [ ] call Ana (normal)
```
