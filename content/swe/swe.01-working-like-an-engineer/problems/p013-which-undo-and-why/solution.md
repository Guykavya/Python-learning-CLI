## Approach

The model answer is in `answer.md`. The decision rule of chapter section 9.1: **if the commit is shared, never rewrite it; add a new commit that undoes it. If it is only yours, you may rewrite.**

Also learn the danger levels: `restore` of a file and `reset --hard` destroy uncommitted work for good; everything committed can usually be recovered from `reflog`.

## Complexity

Not applicable.

## Another way

Practise each situation in a scratch repository (chapter section 9.8) until the command is automatic. Write the eight cases on a card.
