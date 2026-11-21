## Approach

```python
def build_parser():
    p = argparse.ArgumentParser(prog="tidy", description="Tidy a folder safely.")
    p.add_argument("-v", "--verbose", action="count", default=0, help="more output (-vv for debug)")
    p.add_argument("--version", action="version", version="tidy 1.0")
    sub = p.add_subparsers(dest="command", required=True)

    org = sub.add_parser("organize", help="move files into folders by type")
    org.add_argument("folder", type=Path)
    org.add_argument("-n", "--dry-run", action="store_true", help="show what would happen, change nothing")

    und = sub.add_parser("undo", help="reverse the last 'organize'")
    und.add_argument("folder", type=Path)

    dup = sub.add_parser("dupes", help="list files with identical content")
    dup.add_argument("folder", type=Path)
    dup.add_argument("--min-size", type=int, default=1, metavar="BYTES", help="ignore smaller files")
    return p
```

argparse does the boring and error-prone work for you: it converts `"10"` to `10`, refuses `abc` with a clear message and exit code 2, writes the help text and the usage line, and gives `--dry-run` the attribute name `dry_run`.

## Complexity

Parsing is linear in the number of arguments.

## Another way

Click (chapter 5.1) writes the same tool with decorators: `@click.group()` for the tool, `@cli.command()` per subcommand, `@click.option("-v", count=True)`. Problem p010 does that.
