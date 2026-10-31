# Round-trip properties: run-length encoding

If two functions undo each other, the best property you can write is the **round trip**:
`decode(encode(x)) == x` for every `x`. Here is a small run-length codec:

```python
def encode(text):
    """Run-length encode letters: "aaabcc" -> "a3b1c2". Every run is written, even a run of 1.

    Only letters are allowed (anything else raises ValueError).
    """
    if not text.isalpha() and text != "":
        raise ValueError("letters only")
    out = []
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] == text[i]:
            j += 1
        out.append(text[i] + str(j - i))
        i = j
    return "".join(out)


def decode(code):
    """Undo encode: "a3b1c2" -> "aaabcc". The count after a letter can have several digits."""
    out = []
    i = 0
    while i < len(code):
        letter = code[i]
        j = i + 1
        while j < len(code) and code[j].isdigit():
            j += 1
        out.append(letter * int(code[i + 1:j]))
        i = j
    return "".join(out)
```

In `solution.py` write tests (`from target import encode, decode`; save the code above as `target.py`
to try them). Write at least 3 test functions and put
`@settings(derandomize=True, database=None, max_examples=100)` above every `@given`.

Your tests must **pass** on the correct code and **fail** on each of six buggy versions.
The report names the survivor.

Two things to think about:

1. **The strategy decides what you find.** `st.text()` over all of Unicode rarely produces a run of 12 equal letters, and
   it produces digits that `encode` refuses. Choose an alphabet and a shape that make the interesting cases common.
2. **A round trip is not enough.** A buggy encoder paired with a decoder that understands its output still round-trips.
   Some bugs need one plain example test of the encoded text.

**Example**

```python
@settings(derandomize=True, database=None, max_examples=100)
@given(st.text(alphabet="abc", max_size=30))
def test_round_trip(text):
    assert decode(encode(text)) == text, "decode must undo encode."
```

**How this is checked.** Your `solution.py` is copied next to the code above (saved as `target.py`)
and real pytest runs on it: first on the correct code, then on each buggy copy. At least one test must fail on each bug.
