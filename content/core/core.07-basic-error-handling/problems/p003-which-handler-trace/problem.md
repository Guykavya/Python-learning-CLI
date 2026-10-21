# Which handler runs?

Predict **exactly** what this program prints. For each call, first decide which exception (if any)
is raised, then walk down the `except` clauses **in order** and stop at the first match. Keep the
hierarchy from chapter section 4 next to you.

```python
def attempt(label, action):
    try:
        action()
        print(label, "-> no error")
    except KeyError:
        print(label, "-> KeyError handler")
    except LookupError:
        print(label, "-> LookupError handler")
    except ArithmeticError:
        print(label, "-> ArithmeticError handler")
    except (ValueError, TypeError) as e:
        print(label, "->", type(e).__name__, "in the tuple handler")

data = {"a": [1, 2]}
attempt("1", lambda: data["b"])
attempt("2", lambda: data["a"][5])
attempt("3", lambda: 10 % 0)
attempt("4", lambda: int("ten"))
attempt("5", lambda: len(42))
attempt("6", lambda: data["a"][-1])
attempt("7", lambda: [3, 1].index(2))
try:
    attempt("8", lambda: undefined_name)
except NameError as e:
    print("8 escaped as", type(e).__name__)
print("end")
```

Write your answer in `answer.txt`, one line per printed line.
