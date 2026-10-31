# Explain: read the shrunk counterexample

A function `chunk(items, size)` splits a list into consecutive pieces of at most `size` items: `chunk([1, 2, 3, 4, 5], 2)` should give
`[[1, 2], [3, 4], [5]]`. Here is the code and two property tests:

```python
def chunk(items, size):
    """Split items into consecutive lists of at most `size` items."""
    return [items[i:i + size] for i in range(0, len(items) - size, size)]
```

```python
from hypothesis import given, settings, strategies as st

from chunker import chunk


@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers()), st.integers(min_value=1, max_value=5))
def test_chunks_are_not_longer_than_size(items, size):
    assert all(len(part) <= size for part in chunk(items, size))


@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers()), st.integers(min_value=1, max_value=5))
def test_joining_the_chunks_gives_the_items_back(items, size):
    joined = [x for part in chunk(items, size) for x in part]
    assert joined == items
```

This is the output of `python -m pytest -q --tb=short` (run twice with the same result, because of `derandomize=True`; the timing is removed):

```text
.F                                                                       [100%]
=================================== FAILURES ===================================
_________________ test_joining_the_chunks_gives_the_items_back _________________
test_chunker.py:13: in test_joining_the_chunks_gives_the_items_back
    @given(st.lists(st.integers()), st.integers(min_value=1, max_value=5))
                   ^^^
test_chunker.py:16: in test_joining_the_chunks_gives_the_items_back
    assert joined == items
E   assert [] == [0]
E     
E     Right contains one more item: 0
E     Use -v to get more diff
E   Failing test case: test_joining_the_chunks_gives_the_items_back(
E       items=[0],
E       size=1,  # or any other generated value
E   )
=========================== short test summary info ============================
FAILED test_chunker.py::test_joining_the_chunks_gives_the_items_back - assert...
1 failed, 1 passed
```

In `answer.md` (about 250 to 400 words), explain:

1. **Reading the report.** Which test failed and which passed? What does the passing test tell you, and what does it *not* tell you?
2. **The counterexample.** What is hypothesis showing you with `items=[0], size=1`? Hypothesis first found some larger failing input and then **shrank** it: say what
   shrinking does and why the report is better for it.
3. **Why this case is minimal.** Why is the failing input a list of one item and not the empty list? What does the comment `# or any other generated value` after `size=1` tell you about
   the bug?
4. **The bug and the fix.** Trace `chunk([0], 1)` by hand to find the bug, name the mistake, and give the corrected code. Then say which kind of test you would add to keep this bug from coming back.

**Example** of the level of detail expected for one part:

> 1. `test_chunks_are_not_longer_than_size` passed and `test_joining_...` failed. The first only looks at the lengths of the pieces that
> exist, so a function that drops pieces passes it. It says nothing about whether all the items are still there.
