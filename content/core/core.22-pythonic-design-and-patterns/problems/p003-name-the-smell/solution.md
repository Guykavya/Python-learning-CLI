## Approach

The model answer is in `answer.md`. Every smell has the same anatomy: a habit that works in the
easy case, a case where it breaks or misleads, and a small standard fix.

| # | Smell | Breaks when | Fix |
|---|---|---|---|
| 1 | mutable default | second call sees first call's data | `None` default |
| 2 | bare `except` | `Ctrl-C`, typos, real bugs are swallowed | name the exception |
| 3 | `type(x) ==` | subclass or tuple passed | `isinstance` |
| 4 | `+=` string building | large inputs (repeated copying) | `join` |
| 5 | one-letter name | reader must guess | meaningful name |
| 6 | mixed return types | caller forgets the check | `None` or exception |

## Check your answer

- Did you say **when** the default list is created (at `def` time, once)?
- Did you name the exceptions a bare `except` also catches?
- Did you give code for every fix, not just words?
- For 6, did you pick one clear way to say "not found" and say why mixed returns are risky?

## Another way

Linters find most of these for you: `ruff` or `flake8` report B006 (mutable default), E722
(bare except), E721 (type comparison), E741 (ambiguous name `l`). Run one on your own code.
