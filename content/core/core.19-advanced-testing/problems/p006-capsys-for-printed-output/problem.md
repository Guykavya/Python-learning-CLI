# Write tests: capsys and a printed report

A function that **prints** instead of returning cannot be checked with `assert f(x) == ...`.
The built-in **`capsys`** fixture captures everything written to stdout and stderr:
`capsys.readouterr()` returns an object with `.out` and `.err`.

The code under test (it starts with `import sys`):

```python
import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total:.2f}")
```

In `solution.py` (import with `from target import print_report`) write tests that

- **pass** on the code above,
- **fail** on each of eight buggy versions the checker tries (it names the survivor),
- take `capsys` as a parameter in **at least four** tests, and
- contain at least five test functions.

Save the code above as `target.py` next to your `solution.py` and run
`python -m pytest solution.py` to try your tests. Give every `assert` a message.

**Example of one test**

```python
def test_one_sale(capsys):
    print_report([("tea", 2.5)])
    out = capsys.readouterr().out
    assert out == "tea: 2.50\nTOTAL: 2.50\n", "One line per sale, then TOTAL, all with two decimals."
```
