## Approach

`break` is a claim about all the later candidates at once. That claim is only true when the list is sorted. Sorting does not remove answers or (here) calls: the `if c > remaining` check already avoids the call; sorting turns "skip this one" into "skip all the rest".

## Model answer

See `answer.md` and tick the checklist at its end.

## What to check

- Your counter-example really loses an answer.
- You did not claim that sorting changes the set of answers.
- You see the difference between pruning a **call** (the check) and pruning the **loop** (break).
