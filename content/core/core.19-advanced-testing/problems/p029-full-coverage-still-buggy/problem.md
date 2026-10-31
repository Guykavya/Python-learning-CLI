# Explain: 100% coverage, still buggy

A teammate proudly reports "100% line and branch coverage" for `shipping`. Here is the
function, with its specification in the docstring:

```python
def shipping(weight_kg, express):
    """Shipping cost in euros.

    Base cost 5. A parcel of 10 kg or more adds a surcharge of 10.
    Express doubles the BASE cost only (the surcharge is not doubled).
    A negative weight is an error (ValueError).
    """
    cost = 5
    if weight_kg > 10:
        cost += 10
    if express:
        cost *= 2
    return cost
```

The tests, and the report from `python -m coverage run --branch -m pytest -q` followed by `python -m coverage report -m`:

```python
def test_light_standard():
    assert shipping(2, False) == 5

def test_heavy_standard():
    assert shipping(12, False) == 15

def test_light_express():
    assert shipping(2, True) == 10
```

```text
...                                                                      [100%]
3 passed

Name          Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------
shipping.py       7      0      4      0   100%
---------------------------------------------------------
TOTAL             7      0      4      0   100%
```

Yet the function has **three** bugs against its own specification:

```text
shipping(10, False)  ->  5     the spec says 15
shipping(12, True)   ->  30    the spec says 20
shipping(-4, False)  ->  5     the spec says ValueError
```

In `answer.md` (about 250 to 400 words), explain:

1. **What 100% means.** In one or two sentences, say what line coverage and branch coverage actually measure, and which of the two is stronger here.
2. **Why each bug escapes.** For each of the three bugs, say which kind of gap it is and why coverage cannot see it:
   a wrong **boundary**, a combination of paths that was never **run together**, and **code that is missing** altogether.
3. **The tests that would catch them.** Give one new test (call and expected value) for each bug.
4. **A rule of thumb.** What is coverage good for, and what should you do instead of aiming for a number?

**Example** of the level of detail expected for one part:

> 1. Line coverage counts the lines that ran at least once. Branch coverage also asks that every `if` was both true and false.
> Both only say "this code ran", never "this code gave the right answer".
