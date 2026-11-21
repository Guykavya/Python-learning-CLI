## Model answer

**1. Testing.** Every test of this command must go through the command line: a `CliRunner` (or a subprocess), a temporary folder, and string matching on printed text. There is no value to inspect, only output. The dry run is honest only by luck: the "would move" branch and the real branch compute the destination separately, so nothing guarantees they agree. With `plan_moves(root)` returning a list of `(src, dst)` pairs, a test compares two lists, and the dry run prints **the very list** the real run executes. This code also overwrites a file that already sits in the target folder; to test the overwrite rule you would again need the whole CLI, while `unique_destination` is a three-line test.

**2. Two front ends, one core.** With the logic inside the Click command, an argparse version (for a server where no extra package may be installed) must copy it, and every bug must then be fixed twice; one copy will be forgotten (swe.10's lesson about copied rules). With a thin layer, `tidy.py` and `tidy_click.py` both call `plan_moves` and `apply_moves`; a fix in the library fixes both. Moving to Typer costs about 20 lines of new CLI code instead of a rewrite of the tool.

**3. Reuse.** A scheduled job wants `run_job("tidy", lambda: apply_moves(plan_moves(folder), folder), status_dir)`: a function call with a return value it can record in the status file. This command has neither: it reads `sys.argv` through Click, prints instead of returning, and Click calls `sys.exit` at the end. The suite would have to fake a command line and parse printed text.

**4. Where does a change go?** The `.JPG` bug is in the library (`category_for` lower-cases the suffix, or the `CATEGORIES` table). Renaming `--dry-run` to `--preview` touches only the CLI file. If one kind of change forces you to edit both kinds of file, the layers are tangled.

**5. Checklist for a thin CLI layer.**
- [ ] The command function only parses, calls library functions, prints, and returns an exit code.
- [ ] The library never imports `click`, `argparse` or `sys.argv`, and never calls `print` for results or `sys.exit`.
- [ ] Library functions take values (`Path`, `bool`, `int`) and return values (lists, counts), so tests compare data.
- [ ] Decisions are made once (plan), and the dry run prints that plan.
- [ ] Every safety rule (never overwrite, dry run changes nothing, undo) has a test at the library level.
- [ ] A second front end or a scheduled job can call the same functions without a terminal.

**Checklist: your answer should mention**
- [ ] tests of a fat command need a CLI runner and string matching; library tests compare values
- [ ] the dry run is only trustworthy when it prints the same plan the real run executes
- [ ] with two front ends, logic in the CLI means two copies and fixes made twice
- [ ] a scheduled job or suite calls functions, not command lines, and needs return values
- [ ] the chapter's answer: `.JPG` bug in the library, `--preview` rename in the CLI only
- [ ] at least four concrete review rules
