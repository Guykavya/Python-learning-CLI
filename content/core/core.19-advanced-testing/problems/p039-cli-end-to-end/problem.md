# End-to-end test of a command-line tool

A command-line program has three outputs: what it prints, what it prints to standard error, and its **exit code**. A good
design keeps the work in `main(argv) -> int`, which you can call from a test without starting a process. But the last
line of the file (`sys.exit(main())`) can only be tested by really running the program.

```python
import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(prog="wordstat", description="Count the most common words in a text file.")
    parser.add_argument("file", help="path of a UTF-8 text file")
    parser.add_argument("--top", type=int, default=5, help="how many words to show (default 5)")
    parser.add_argument("--min-length", type=int, default=1, help="ignore shorter words (default 1)")
    parser.add_argument("--json", action="store_true", help="print a JSON object instead of lines")
    return parser


def main(argv=None):
    """Run the tool. Return the exit code: 0 success, 2 when the file cannot be read."""
    args = build_parser().parse_args(argv)
    try:
        text = Path(args.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"wordstat: no such file: {args.file}", file=sys.stderr)
        return 2
    counts = Counter()
    for raw in text.lower().split():
        word = raw.strip(".,;:!?")
        if word and len(word) >= args.min_length:
            counts[word] += 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: args.top]
    if args.json:
        print(json.dumps(dict(ranked)))
    else:
        for word, n in ranked:
            print(f"{word} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

In `solution.py` write tests (`import wordstat`; save the code above as `wordstat.py` to try them). Write at least 7 test functions:

- call `wordstat.main([...])` directly, with `tmp_path` for the input files and `capsys` for the output;
- check the printed lines, the JSON, the return code, and that errors go to **standard error**;
- write **one** test that starts the real program with
  `subprocess.run([sys.executable, wordstat.__file__, ...], capture_output=True, text=True, timeout=30)` and checks `returncode`.
  Always use `sys.executable`, never the word `"python"`, so the same Python runs.

Your tests must **pass** on the correct code and **fail** on each of ten buggy versions. The report names the survivors. One bug only
shows when the program is run as a script.

**Example**

```python
def test_missing_file(tmp_path, capsys):
    assert wordstat.main([str(tmp_path / "nope.txt")]) == 2, "A missing file returns 2."
    assert "nope.txt" in capsys.readouterr().err, "The message goes to standard error."
```

**How this is checked.** Your `solution.py` is copied next to the code above (saved as `wordstat.py`)
and real pytest runs on it: first on the correct code, then on each buggy copy. At least one test must fail on each bug.
