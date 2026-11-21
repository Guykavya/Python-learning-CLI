# Contract tests that catch a lying fake

Chapter section 6.3 (fakes can lie: contract tests) and "Try it: the repository for a one-table app". In p006 the contract tests were given to you. Now **you write them**. A contract test is only worth something if it would fail for a fake that lies, so this problem tests your tests: they must **pass** on honest repositories and **fail** on lying ones.

## The interface

A `ProjectRepo` stores who belongs to a project. People are identified by a **handle** (a string such as `"Ana"`), and handles are compared **without regard to case**:

```python
repo.add_member(project_id, handle)        # idempotent: adding the same person twice is the same as adding once
repo.is_member(project_id, handle) -> bool # False for a person who was never added, or for another project; case-insensitive
repo.members(project_id) -> list[str]      # the handles of that project, in lower case, sorted, without duplicates
```

The tests give you three honest-or-lying implementations to run against (you do not see their code; you see their **behaviour** through your checks):

- the real **SQLite** repository and an **honest fake**: your checks must pass on both;
- three **lying fakes**; each one breaks one rule of the interface:
  1. **duplicating**: adding the same member twice stores two entries;
  2. **case-sensitive**: `"Ana"` and `"ana"` are different people, and handles are stored as given;
  3. **project-blind**: membership ignores which project it is about.

## What to write

In `solution.py`, write **check functions** and list them in `CHECKS`:

```python
def check_adding_twice_is_the_same_as_once(repo):
    repo.add_member(1, "ana")
    repo.add_member(1, "ana")
    assert repo.members(1) == ["ana"], "adding the same member twice must not create a duplicate"

CHECKS = [check_adding_twice_is_the_same_as_once, ...]
```

Rules for your checks:

- Each check takes a **fresh, empty repository** (the tests build a new one for every check, so no clean-up is needed) and uses only the three methods above.
- A check **raises `AssertionError`** with a **message that names the broken rule** when the repository lies, and does nothing when it is honest. Anything else (an `AttributeError`, a wrong method name) is a bug in your check.
- Write **at least 4** checks. The tests then require: every check passes on both honest repositories, and **each lying fake is caught by at least one check**. Think about what a lie would look like first; then write the smallest check that exposes it.

## Example

The check above passes on SQLite and on the honest fake, and fails on the duplicating fake (`members(1)` is `['ana', 'ana']`). It does not catch the other two lies: you still need checks for case and for isolation between projects.
