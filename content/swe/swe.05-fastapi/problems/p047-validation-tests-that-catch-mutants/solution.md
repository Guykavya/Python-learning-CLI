## Approach

Test every limit from both sides, one rule per payload.

```python
CASES = [
    # valid, including both edges of every range
    ({"title": "Write tests"}, 201),
    ({"title": "x"}, 201),                                      # shortest allowed title
    ({"title": "x" * 100}, 201),                                # longest allowed title
    ({"title": "a", "priority": 1, "tags": ["work"]}, 201),     # lowest priority
    ({"title": "a", "priority": 5}, 201),                       # highest priority
    # invalid: one step past each limit
    ({"title": ""}, 422),                                       # too short
    ({"title": "x" * 101}, 422),                                # too long
    ({"title": "a", "priority": 0}, 422),
    ({"title": "a", "priority": 6}, 422),
    # other rules
    ({"priority": 2}, 422),                                     # title missing
    ({"title": "a", "owner": "asha"}, 422),                     # unknown field
    ({"title": "a", "tags": "work"}, 422),                      # tags must be a list
]
```

How each mutant dies:

| Mutant | The case that catches it |
|---|---|
| empty titles accepted | `{"title": ""}`: expected 422, the mutant answers 201 |
| title limit 101 | `"x" * 101`: expected 422, the mutant answers 201. (A test with 200 characters would **not** catch it: both refuse.) |
| priority up to 6 | `priority: 6`: expected 422, the mutant answers 201. (`priority: 9` would not catch it.) |
| unknown fields ignored | `{"title": "a", "owner": "asha"}`: expected 422, the mutant answers 201 |

The valid cases on the edges (`"x"`, `"x" * 100`, priorities 1 and 5) catch the **opposite** kind of mutant, one that tightens a rule by mistake (`max_length=99`). The real test suite needs both.

## Complexity

One request per case per app: 12 cases × 5 apps = 60 in-process requests, well under a second.

## Another way

Real mutation testing tools (`mutmut`, `cosmic-ray`) generate the mutants **automatically** from your source code (change `<` to `<=`, `1` to `2`, delete a line...), run your test suite against each, and report the survivors. It is slow on a big project, so teams run it on the most important modules. Property-based testing (Hypothesis, which is installed) is the other way to find holes: it searches for inputs that break a rule you state, and it shrinks a failing input to the smallest one.
