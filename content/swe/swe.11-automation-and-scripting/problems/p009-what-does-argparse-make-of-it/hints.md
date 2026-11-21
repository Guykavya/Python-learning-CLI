## Hint 1

Go word by word. Options added to `p` are understood only **before** the subcommand word; after `organize`, the `organize` sub-parser takes over and knows only `folder`, `-n/--dry-run` and `-h`. A word it does not know ends in "unrecognized arguments". Which attributes exist in the `Namespace`? Only those of the main parser plus those of the chosen subcommand (with their defaults).

## Hint 2

For each line ask three questions: (1) is every required positional present? (2) does every value convert (`type=int`)? (3) is every option known **in the place where it appears**? One "no" means `exit 2`. Otherwise list: `command`, the subcommand's own attributes (`dry_run` or `min_size`), `folder`, `verbose`, sorted alphabetically. A quoted `"old photos"` reaches Python as one word.
