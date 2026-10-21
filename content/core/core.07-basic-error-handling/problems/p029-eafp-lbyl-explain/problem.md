# Explain: look before you leap?

Two students wrote the same helper:

```python
def read_quantity_a(text):
    if text.isdigit():
        return int(text)
    return None

def read_quantity_b(text):
    try:
        return int(text)
    except ValueError:
        return None
```

In `answer.md`:

1. Name the two styles (full names and abbreviations) and say which function uses which.
2. Give **three** inputs on which the two functions behave differently, and say what each
   returns (or raises) for each input. Include at least one where version A **crashes**.
3. A third student checks a file before opening it:
   `if os.path.exists(name): f = open(name)`. Explain why this can still fail with
   `FileNotFoundError`, using the term **race condition** (or time of check to time of use), and
   say what the EAFP version looks like and why it does not have the problem.
4. Give **two** situations where LBYL is the better choice, with a reason for each.
