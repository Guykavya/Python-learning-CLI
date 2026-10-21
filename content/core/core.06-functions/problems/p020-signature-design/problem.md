# Design a signature that is hard to misuse

A banking script has this function:

```python
def transfer(amount, from_acct, to_acct, notify, fee=[]):
    ...
```

and these calls appear in the code base:

```python
transfer(500, "SAV-1", "CUR-9", True)
transfer(500, "CUR-9", "SAV-1", False)
transfer(250, "SAV-1", "CUR-9", False, [10])
```

In `answer.md`, explain in your own words:

1. Two different ways a programmer could call `transfer` wrongly **without** Python noticing,
   and what would happen.
2. What is wrong with `fee=[]`, and what you would use instead.
3. Rewrite the `def` line using `/` and/or `*` and defaults so those mistakes become impossible
   or obvious. Justify each choice (which parameters are positional-only, which keyword-only,
   which have defaults, and why).
4. Rewrite the three calls for your new signature.
5. One general rule of thumb for designing a signature that is hard to misuse.
