## Approach

Review from the outside in: first the **data** (who owns it, is it shared, is it checked), then the
**errors** (are they visible and specific), then the **responsibilities** (how many reasons does this
class have to change). The redesign uses nearly every idea of the module: instance vs class attributes
(section 5), classmethod constructors (section 6), properties (section 8), composition vs inheritance
(section 14), polymorphism and duck typing (section 15) and an exception hierarchy with chaining
(sections 17 and 18).

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Refactor in small, safe steps instead of a rewrite: (1) write tests for today's behaviour of `fee` and
`grade`; (2) move `students` into `__init__`; (3) replace the bare `except` with a specific one that
raises `LoadError`; (4) extract `Student` with `from_row`; (5) extract the fee policies; (6) pass the
mailer in. After every step the tests must still pass. This is how real code bases get out of a God
class.
