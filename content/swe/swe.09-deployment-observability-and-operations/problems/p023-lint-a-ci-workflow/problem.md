# Lint a CI workflow

Chapter sections 11.3 (CI is just commands: put them in a Makefile), 11.4 (the workflow file) and 11.5 (lint your CI before GitHub does). A workflow with a mistake tells you only after a push, in a browser tab. Write a small linter for **GitHub Actions workflow files** that runs on your laptop. GitHub is never contacted: the tests give you the YAML text (read with PyYAML) or the already parsed dictionary.

A YAML 1.1 trap: PyYAML reads the key `on` as the boolean **`True`**, so the triggers of a workflow arrive as `workflow[True]`. Look under both `"on"` and `True`.

## What to write

```python
def check(workflow: dict) -> list[tuple[str, str]]: ...
```

It returns `(severity, message)` pairs, severity being `"error"` or `"warning"`. The **messages are yours**, but each must contain the **keyword** of its rule (a substring, case-sensitive) so a person can search for it. The rules, exactly (these are the only rules):

| Where | Condition | Severity | Keyword |
|---|---|---|---|
| workflow | no triggers (`on` / `True`) missing or empty | error | `trigger` |
| workflow | the triggers are a mapping containing `pull_request_target` (it runs with secrets on code from forks) | error | `pull_request_target` |
| workflow | no top-level `permissions` | warning | `permissions` |
| workflow | no jobs (missing or empty `jobs`) | error | `no jobs` |
| a job | no `runs-on` | error | `runs-on` |
| a job | no `timeout-minutes` (a hung job runs for 6 hours) | warning | `timeout-minutes` |
| a job | `needs` (a string or a list) names a job that does not exist | error | `needs` |
| a step | `uses` without `@` and not a local action (`./...`) | error | `no version` |
| a step | `uses: x@ref` where `ref` is `main`, `master`, `latest` or `HEAD` | error | `moving` |
| a step | `uses: x@ref` where `x` does not start with `actions/` or `docker/` and `ref` is not a 40-character hex commit SHA | warning | `commit SHA` |
| a step | a `run` script containing `${{ secrets.` (write `${{`, optional spaces, `secrets.`; pass secrets through `env:`) | error | `secret` |
| a step | `uses: actions/cache@...` whose `with.key` does not contain `hashFiles(` (a cache key must change when the lock file changes) | warning | `hashFiles` |
| workflow | no step in any job whose `run` contains `make test` (CI should run the **same command** as developers: the Makefile of section 11.3) | warning | `make test` |

A **local action** (`uses: ./.github/actions/setup`) is never checked for versions or pinning. A step without `uses` or `run`, or a job whose value is not a mapping, must not crash the linter. Report each finding once per place (a job missing both `runs-on` and `timeout-minutes` gives two findings).

## Example

```python
check(yaml.safe_load(CHAPTER_CI_YML))      # the workflow of chapter 11.4
# []
check(yaml.safe_load('''
name: bad
on:
  pull_request_target:
jobs:
  build:
    needs: test
    steps:
      - uses: actions/checkout
      - uses: someone/deploy-action@main
      - run: curl -H "token: ${{ secrets.DEPLOY_KEY }}" https://example.com
'''))
# [('error', 'pull_request_target ...'), ('warning', 'no top-level permissions ...'), ('error', "job 'build' has no runs-on"), ... , ('warning', 'no step runs make test ...')]
```
