## Approach

The model answer is in `answer.md`. The principle is: **a commit is a unit that other tools handle** (revert, bisect, cherry-pick, review). A tool can only do a precise job on a precise commit.

You can clean a messy local history before sharing it with interactive rebase (chapter section 7): `squash` the fixups, `reword` the messages, `drop` the junk file.

## Complexity

Not applicable.

## Another way

Think of commits as paragraphs: one idea each, in an order that tells a story. Nobody can quote a paragraph that is half a different idea.
