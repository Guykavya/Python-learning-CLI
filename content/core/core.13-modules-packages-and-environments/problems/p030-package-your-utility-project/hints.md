## Hint 1

Split the work into three parts and do them in this order: (1) **check** every argument and the
target folder, and raise before anything is written; (2) **build the text** of every file;
(3) **write** the files. Which file texts are always the same, and which need the name, the package
or the version put into them?

## Hint 2

Keep each generated file as a template string at the top of `solution.py`, with placeholders that
cannot appear in normal code, like `__NAME__`, `__PKG__`, `__VERSION__`. Fill them with
`.replace(...)`. (With `.format()` or f-strings, every `{` and `}` in the generated code would have to
be doubled.)

Build `pyproject.toml` line by line, and write every string value with a helper:

```text
def toml_string(value): return json.dumps(value)        # "...", with \" and \\ escaped
def toml_list(values):  return "[" + ", ".join(toml_string(v) for v in values) + "]"
lines = ["[build-system]", 'requires = ["setuptools>=61"]', ..., f"name = {toml_string(name)}", ...]
```

## Hint 3

The generated `cli.py`:

```text
from . import __version__
from .core import slugify, word_count

def build_parser():
    parser = ArgumentParser(prog="__NAME__")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    slug: add_argument("text", nargs="+")
    count: add_argument("file", nargs="?", default="-")

def main(argv=None):
    args = build_parser().parse_args(argv)
    slug  -> print(slugify(" ".join(args.text))); return 0
    count -> read stdin if file == "-", else open it (OSError -> print error to stderr, return 1)
             print(word_count(text)); return 0
```

The generated `__main__.py` is four lines: `import sys`, `from .cli import main`, and
`if __name__ == "__main__": sys.exit(main())`.

## Hint 4

Inside a `'''...'''` template in `solution.py`, a `\n` becomes a real line break in the generated
file. In the generated test, `"three\n"` must stay a backslash-n, so write `"three\\n"` in the
template. Run your generator once into a scratch folder and look at the files before you run the tests.
