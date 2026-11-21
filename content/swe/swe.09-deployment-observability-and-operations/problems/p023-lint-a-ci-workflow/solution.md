## Approach

The full code is `reference.py`. It follows the structure of the chapter's `check` function (workflow level, job level, step level) and adds the two rules from the plan of the module (the cache key, `make test`). The three places where it differs from the chapter's code:

```python
if uses and not uses.startswith("./"):          # local actions are never checked
    if "@" not in uses:
        ...("error", ... "no version" ...)
    else:
        action, ref = uses.split("@", 1)
        ...
```

- The chapter's version evaluates `uses.split("@", 1)[1]` for any `uses` that is not an error case; for a **local action** (`./.github/actions/setup`, no `@`) that raises `IndexError`. The rule "local actions are skipped" avoids it.
- Steps without `uses` or `run`, and jobs that are `null` in the YAML, are skipped instead of crashing.
- The `make test` rule needs a flag collected across all jobs and reported once at the end.

Why each rule matters (chapter 11): `pull_request_target` runs with secrets on a fork's code; a moving ref such as `@main` lets the action's author (or an attacker who compromises them) change what runs with your secrets; secrets pasted into scripts can be echoed; a missing timeout lets a hung job run for six hours; and a CI file that runs different commands than the developers do is a CI file that fails for reasons nobody can reproduce locally.

## Complexity

O(size of the workflow).

## Another way

`actionlint` (the chapter shows how to run it in Docker) knows the whole workflow syntax, expressions included. A small checker like this one is still valuable for **your own policies** (the cache key, `make test`), which no general linter knows.
