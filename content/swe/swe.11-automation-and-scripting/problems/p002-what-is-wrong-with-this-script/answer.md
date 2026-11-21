## Model answer

1. **Hard-coded folder.** It works on one machine for one user. On the server, or for a colleague, `C:/Users/me/Downloads` does not exist, so `os.listdir` crashes (or, worse, someone edits the code and commits their own path). **Fix:** take the folder as an argument (`p.add_argument("folder", type=Path)`), with a default from a config file or environment variable (section 8).
2. **No dry run, no undo.** The first run on a real folder is the test. If the rule is wrong (it moved invoices someone else needed), there is no record of what moved where. **Fix:** split *plan* from *do*: `plan_moves()` returns (source, destination) pairs and changes nothing, `--dry-run` prints the plan, and the real run writes a journal so `undo` can reverse it (rules 1 and 2 of section 1.3).
3. **`print` for errors.** Error lines go to stdout, mixed with any real output; `bad_tidy.py | wc -l` or `| sort` treats them as data. Under cron stdout is often lost, so nobody ever sees them. **Fix:** `logging` to stderr and to a log file (`log.error("could not move %s: %s", f, e)`); keep stdout for data.
4. **Exit code 0 on failure.** The `except` swallows every error and the script ends with "done", so the shell, cron, CI and any monitor see success. Ten failed moves look like a perfect night. **Fix:** count failures and `return 1` from `main()` when there were any; `sys.exit(main())` passes it on (section 2.3). Catch only the errors you can handle (`OSError`), and let bugs show a traceback.
5. **Relative destination.** `"pdfs/" + f` is relative to the **current working directory**, not to the Downloads folder. Started from your home folder it creates `~/pdfs`; under cron (whose working directory is your home) the same; started from another folder it scatters PDFs there. If `pdfs/` does not exist, every move fails. **Fix:** build every path from the input folder (`folder / "pdfs" / name`) and create it with `mkdir(parents=True, exist_ok=True)`.
6. **Gluing paths with `+`.** Double slashes, missing slashes and backslash/slash mixtures on Windows. **Fix:** `pathlib.Path` and the `/` operator.
7. **Overwriting.** If `pdfs/invoice.pdf` already exists, `shutil.move` may silently replace it (depending on the system), destroying a file for ever. **Fix:** `unique_destination()` gives `invoice (1).pdf`; never overwrite.
8. **More problems** (any one): it runs when imported, so it cannot be tested (put the work in functions and use `if __name__ == "__main__":`); `.PDF` in capitals is missed (`suffix.lower()`); `except Exception` also hides bugs such as a typo; no lock, so two runs at once fight over the same files; no log file, so a 3 a.m. failure leaves no trace.

**The skeleton:**

```python
log = logging.getLogger("tidy")

def plan_moves(folder): ...          # returns [(src, dst)], changes nothing
def apply_moves(moves, folder, dry_run): ...   # moves, writes a journal

def build_parser():
    p = argparse.ArgumentParser(prog="tidy")
    p.add_argument("folder", type=Path)
    p.add_argument("-n", "--dry-run", action="store_true")
    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if not args.folder.is_dir():
        log.error("%s is not a folder", args.folder); return 1
    try:
        apply_moves(plan_moves(args.folder), args.folder, args.dry_run)
    except OSError as e:
        log.error("%s", e); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Checklist: your answer should mention**
- [ ] the folder as an argument (or config), not a constant
- [ ] dry run by planning first, and a journal for undo
- [ ] errors to stderr / logging, data to stdout
- [ ] a non-zero exit code when something failed, and why cron and CI need it
- [ ] the working directory: relative paths depend on where the script is started (cron starts in your home)
- [ ] `pathlib` instead of `+ "/"`
- [ ] never overwrite: a unique destination name
- [ ] at least one extra problem (import runs it, `.PDF`, broad `except`, no lock, no log file)
