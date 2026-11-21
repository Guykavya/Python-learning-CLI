## Hint 1

Arguments added to the main parser `p` are global and must come **before** the subcommand; arguments added to a sub-parser belong to that subcommand only. Which `action` counts how often a flag appears? Which one turns a flag into `True`? Look at the table of section 3.1.

## Hint 2

```text
p = ArgumentParser(prog="tidy")
p.add_argument("-v", "--verbose", action="count", default=0)
p.add_argument("--version", action="version", version="tidy 1.0")
sub = p.add_subparsers(dest="command", required=True)
org = sub.add_parser("organize", help=...); org.add_argument("folder", type=Path); org.add_argument("-n", "--dry-run", action="store_true")
und = sub.add_parser("undo", help=...);     und.add_argument("folder", type=Path)
dup = sub.add_parser("dupes", help=...);    dup.add_argument("folder", type=Path); dup.add_argument("--min-size", type=int, default=1, metavar="BYTES")
```
