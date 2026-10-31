## Hint 1

Which attribute of `sys` is the input stream, and when must you look it up: at import time or inside `main`? How
do you split a line into words when there are commas, dots and digits in it? How do you sort by two keys
where one is descending?

## Hint 2

```
parser = argparse.ArgumentParser(...)
parser.add_argument("files", nargs="*"); "-n", "--top", type=int, default=10; "--min", type=int, default=1
args = parser.parse_args(argv)
if args.top < 1: parser.error("...")
counts = {}
sources = args.files or ["-"]
for name in sources:
    if name == "-": count_lines(sys.stdin, counts)
    else: try open(...) except OSError: print error to stderr; return 2
items = [(w, c) for w, c in counts.items() if c >= args.min]
items.sort(key=lambda item: (-item[1], item[0]))
```
A word generator: walk through the characters of `line.lower()`; keep letters and `'` in a list; a different character ends the word.
