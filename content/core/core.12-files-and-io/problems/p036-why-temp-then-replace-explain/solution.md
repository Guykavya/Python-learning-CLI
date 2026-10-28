## Approach

Think of the file as having two states: "old and complete" and "new and complete". The simple `open(path, "w")`
passes through a third, bad state ("empty or half written"). The temp-then-replace pattern makes sure that the
real name only ever points at a complete file. The switch itself is one directory change, which the operating
system does as one step.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Keep a backup: copy `path` to `path.bak` first and write the new content directly. After a crash you can
restore the backup by hand. This is simpler but needs a person to notice the problem and fix it.
