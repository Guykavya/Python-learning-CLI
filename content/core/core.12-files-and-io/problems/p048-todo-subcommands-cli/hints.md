## Hint 1

Which `argparse` method creates subcommands, and how do you make one of them required? Where do you store which
subcommand was chosen (look at the `dest` argument)? Which argparse feature gives you a list of allowed values, and which
one makes two options exclusive?

## Hint 2

```
parser = ArgumentParser(); parser.add_argument("--file", required=True)
sub = parser.add_subparsers(dest="command", required=True)
p_add = sub.add_parser("add"); text; --priority choices=[...] default="normal"
p_list = sub.add_parser("list"); group = p_list.add_mutually_exclusive_group(); --all, --done  (action="store_true")
p_done = sub.add_parser("done"); id type=int
p_rm   = sub.add_parser("remove"); id type=int
args = parser.parse_args(argv)
todos = load(args.file)
if args.command == "add": ... elif ...
save(args.file, todos) only when something changed
```
