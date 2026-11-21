import textwrap

import pytest
import yaml

from solution import check

CHAPTER_CI = textwrap.dedent('''
    name: ci
    on:
      push:
        branches: [main]
        tags: ["v*"]
      pull_request:
      workflow_dispatch:
    permissions:
      contents: read
    concurrency:
      group: ci-${{ github.ref }}
      cancel-in-progress: true
    jobs:
      test:
        runs-on: ubuntu-latest
        timeout-minutes: 10
        strategy:
          fail-fast: false
          matrix:
            python-version: ["3.13", "3.14"]
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: ${{ matrix.python-version }}
              cache: pip
          - name: Install dependencies
            run: pip install -r requirements.txt pytest httpx mypy
          - name: Type check
            run: make typecheck
          - name: Tests
            run: make test
      image:
        needs: test
        runs-on: ubuntu-latest
        timeout-minutes: 15
        permissions:
          contents: read
          packages: write
        steps:
          - uses: actions/checkout@v4
          - uses: docker/setup-buildx-action@v3
          - name: Log in to GitHub Container Registry
            if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
            uses: docker/login-action@v3
            with:
              registry: ghcr.io
              username: ${{ github.actor }}
              password: ${{ secrets.GITHUB_TOKEN }}
          - name: Build (and push on main or on a version tag)
            uses: docker/build-push-action@v6
            with:
              context: .
              push: ${{ github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v') }}
              tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
              build-args: APP_VERSION=${{ github.sha }}
''')

BAD = textwrap.dedent('''
    name: bad
    on:
      pull_request_target:
    jobs:
      build:
        needs: test
        steps:
          - uses: actions/checkout
          - uses: someone/deploy-action@main
          - run: |
              curl -H "token: ${{ secrets.DEPLOY_KEY }}" https://example.com
''')

SHA = "a" * 40


def load(text):
    return yaml.safe_load(text)


def one_job(steps_yaml, extra_job="", top="permissions:\n  contents: read\n"):
    """A workflow with a single, otherwise correct job whose steps are given. It always runs make test."""
    body = textwrap.indent(textwrap.dedent(steps_yaml).strip(), "      ")
    return load(f"on: push\n{top}jobs:\n  test:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n{extra_job}    steps:\n{body}\n      - run: make test\n")


def keywords(result):
    return sorted((severity, next((k for k in KEYS if k in message), message)) for severity, message in result)


KEYS = ["pull_request_target", "trigger", "permissions", "no jobs", "runs-on", "timeout-minutes", "needs", "no version", "moving",
        "commit SHA", "secret", "hashFiles", "make test"]


def test_the_chapter_workflow_is_clean():
    assert check(load(CHAPTER_CI)) == [], "The workflow of chapter 11.4 follows every rule: expected []. Remember that `on` arrives as the key True."


def test_the_bad_workflow_of_the_chapter():
    result = check(load(BAD))
    assert keywords(result) == sorted([
        ("error", "pull_request_target"), ("warning", "permissions"), ("error", "runs-on"), ("warning", "timeout-minutes"),
        ("error", "needs"), ("error", "no version"), ("error", "moving"), ("error", "secret"), ("warning", "make test"),
    ]), f"The chapter's bad workflow has nine findings (6 errors in the chapter plus the cache and make rules do not apply); got {result}"


def test_result_pairs_are_severity_and_text():
    for pair in check(load(BAD)):
        assert isinstance(pair, tuple) and pair[0] in ("error", "warning") and isinstance(pair[1], str), f"Each finding is (severity, message); got {pair!r}"


def test_the_on_key_is_true_in_yaml_1_1():
    assert True in load("on: push\njobs: {}"), "(Background: PyYAML turns `on` into True; your code must look there.)"
    workflow = {"name": "x", "jobs": {}}
    assert ("error", "trigger") in keywords(check(workflow)), "No `on` and no True key: report that there is no trigger."
    assert all("trigger" not in m for _, m in check(load("on: push\njobs: {}"))), "A workflow with `on: push` has a trigger."
    assert ("error", "trigger") in keywords(check({"on": {}, "jobs": {}})), "An empty trigger section is no trigger."


def test_pull_request_target_only_in_a_mapping():
    workflow = load("on:\n  pull_request_target:\n    types: [opened]\njobs: {}")
    assert ("error", "pull_request_target") in keywords(check(workflow))
    assert ("error", "pull_request_target") not in keywords(check(load("on: pull_request\njobs: {}"))), "A plain string trigger is not pull_request_target."


def test_permissions_rule():
    assert ("warning", "permissions") in keywords(check(one_job("- run: echo hi", top="")))
    assert ("warning", "permissions") not in keywords(check(one_job("- run: echo hi")))


def test_job_rules():
    workflow = load("on: push\npermissions: {}\njobs:\n  a:\n    steps:\n      - run: make test\n  b:\n    runs-on: x\n    timeout-minutes: 1\n    needs: [a, ghost]\n    steps:\n      - run: make test\n")
    got = keywords(check(workflow))
    assert got == sorted([("error", "runs-on"), ("warning", "timeout-minutes"), ("error", "needs")]), f"Job a lacks runs-on and timeout; job b needs 'ghost'; got {got}"


def test_needs_as_a_string():
    workflow = load("on: push\npermissions: {}\njobs:\n  a:\n    runs-on: x\n    timeout-minutes: 1\n    needs: ghost\n    steps:\n      - run: make test\n")
    assert ("error", "needs") in keywords(check(workflow)), "`needs` may be a single string."


@pytest.mark.parametrize("uses, expected", [
    ("actions/checkout@v4", None),
    ("docker/login-action@v3", None),
    ("./.github/actions/setup", None),
    ("actions/checkout", ("error", "no version")),
    ("someone/action", ("error", "no version")),
    ("actions/checkout@main", ("error", "moving")),
    ("someone/deploy-action@latest", ("error", "moving")),
    ("someone/action@HEAD", ("error", "moving")),
    ("someone/action@v2", ("warning", "commit SHA")),
    ("someone/action@" + SHA, None),
    ("someone/action@" + "g" * 40, ("warning", "commit SHA")),
    ("someone/action@" + SHA[:39], ("warning", "commit SHA")),
])
def test_uses_rules(uses, expected):
    result = keywords(check(one_job(f"- uses: {uses}")))
    assert result == ([expected] if expected else []), f"uses: {uses}: expected {expected}, got {result}"


def test_secret_in_run():
    assert ("error", "secret") in keywords(check(one_job('- run: curl -H "token=${{ secrets.KEY }}" x')))
    assert ("error", "secret") in keywords(check(one_job('- run: echo ${{secrets.KEY}}'))), "Optional spaces inside the braces."
    ok = one_job("- run: ./deploy.sh\n  env:\n    KEY: ${{ secrets.KEY }}")
    assert check(ok) == [], "A secret passed through env: is the safe way and is not a finding."


def test_cache_key_must_hash_the_lock_file():
    bad = one_job("- uses: actions/cache@v4\n  with:\n    path: ~/.cache/pip\n    key: pip-cache")
    good = one_job("- uses: actions/cache@v4\n  with:\n    path: ~/.cache/pip\n    key: pip-${{ hashFiles('requirements.txt') }}")
    assert keywords(check(bad)) == [("warning", "hashFiles")], "A constant cache key never changes when dependencies do."
    assert check(good) == []
    nokey = one_job("- uses: actions/cache@v4\n  with:\n    path: x")
    assert ("warning", "hashFiles") in keywords(check(nokey)), "A cache step without a key is also a finding."


def test_ci_must_run_make_test():
    workflow = load("on: push\npermissions: {}\njobs:\n  t:\n    runs-on: x\n    timeout-minutes: 1\n    steps:\n      - run: pytest -q\n")
    assert keywords(check(workflow)) == [("warning", "make test")], "Running pytest directly means CI and developers run different commands."
    assert check(load("on: push\npermissions: {}\njobs:\n  t:\n    runs-on: x\n    timeout-minutes: 1\n    steps:\n      - run: |\n          pip install .\n          make test\n")) == []


def test_no_jobs():
    assert keywords(check(load("on: push\npermissions: {}"))) == [("error", "no jobs")], "No jobs: that single error (no 'make test' warning on top)."


def test_odd_shapes_do_not_crash():
    workflow = load("on: push\npermissions: {}\njobs:\n  a: null\n  b:\n    runs-on: x\n    timeout-minutes: 1\n    steps:\n      - name: only a name\n      - run:\n      - run: make test\n")
    assert check(workflow) == [], "A job that is null and steps without uses or run must not crash the linter."
