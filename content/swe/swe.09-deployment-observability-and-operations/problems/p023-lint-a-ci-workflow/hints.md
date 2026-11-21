## Hint 1

Walk the three levels: the workflow (triggers, permissions, jobs), each job (runs-on, timeout, needs), each step (uses, run). Start with the rules of the chapter's 11.5 code, which you can read in the chapter, then add the two new ones (cache key, `make test`). Where does a local action `./...` need to be skipped so that you do not crash on a missing `@`?

## Hint 2

```text
triggers = workflow.get("on", workflow.get(True))
for each job (skip if not a dict): runs-on, timeout-minutes, needs (str or list)
for each step (skip if not a dict):
    uses: local ./ -> nothing; no "@" -> "no version"; ref in MOVING -> "moving";
          third-party and not 40 hex -> "commit SHA"; actions/cache without hashFiles( in with.key -> "hashFiles"
    run: regex r"\$\{\{\s*secrets\." -> "secret";  r"\bmake\b[^\n]*\btest\b" -> remember that make test is run
at the end: jobs exist and no make test anywhere -> warning
```
