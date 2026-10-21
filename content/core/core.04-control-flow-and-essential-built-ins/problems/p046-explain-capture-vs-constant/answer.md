**What a bare name means.** In a `case`, a plain name such as `YES` is a **capture pattern**.
It does not mean "the value stored in `YES`". It means "match **anything**, and store the
subject in a variable called `YES`". It always succeeds.

**Why the first version is a SyntaxError.** Since `case YES:` matches every possible answer,
the `case NO:` below it could never run. Python checks for this when it compiles the file
and stops with:

```
SyntaxError: name capture 'YES' makes remaining patterns unreachable
```

It says *name capture*: Python is telling you that `YES` is being captured, not compared.

**Why the "fixed" version says Saving for everything.** With `case YES:` followed only by
`case _:`, nothing is unreachable in the compiler's eyes, so it runs. But `case YES:` still
matches every answer, so the wildcard never runs and every answer prints `Saving`. Worse,
the capture **rebinds** `YES`: after typing `n`, `YES` holds `"n"`. Any later code that uses
`YES` is now wrong as well. This is a silent bug.

**Python's rule.** A name **with a dot** (`Answers.YES`, `string.digits`) is a *value
pattern*: Python looks up its value and compares with `==`. A name **without a dot** is a
capture. (`_` is special: it matches anything and binds nothing.)

**Correct versions.**

```python
match answer:              # 1. literals
    case "y":
        print("Saving")
    case "n":
        print("Not saving")

class Answers:             # 2. dotted constants
    YES = "y"
    NO = "n"

match answer:
    case Answers.YES:
        print("Saving")
    case Answers.NO:
        print("Not saving")

match answer:              # 3. guards
    case a if a == YES:
        print("Saving")
    case a if a == NO:
        print("Not saving")

if answer == YES:          # 4. plain if/elif, which is honestly the clearest here
    print("Saving")
elif answer == NO:
    print("Not saving")
```

**Why Python works this way.** Capturing is the whole point of pattern matching:
`case ["go", direction]:` must create `direction`. If bare names were sometimes comparisons
(when a variable of that name exists) and sometimes captures, the meaning of a pattern would
depend on what variables happen to exist elsewhere in the program, and adding an unrelated
variable could silently change a `case`. One fixed rule, "bare names capture, dotted names
compare", avoids that.

Key ideas to check: capture pattern matches anything and binds; the exact SyntaxError text;
silent rebinding in the last case; the dot rule; several fixes; the design reason.
