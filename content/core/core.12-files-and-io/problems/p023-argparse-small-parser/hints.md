## Hint 1

Which method of the parser takes your own list instead of `sys.argv`? How do you say "one or more values", "a flag", and "only these choices"?

## Hint 2

```
parser = argparse.ArgumentParser(prog="tidy")
parser.add_argument("paths", nargs="+")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("--limit", type=int, default=10)
parser.add_argument("--mode", choices=["copy", "move"], default="copy")
return parser.parse_args(argv)
```
