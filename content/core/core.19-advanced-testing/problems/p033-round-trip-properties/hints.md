## Hint 1

Start with the round trip over `st.text(alphabet="abc", max_size=30)`. Then ask: which bugs does it miss? Try writing a
buggy `decode` that only reads one digit and see whether any of your inputs has a run longer than 9. How would you build a text that
has such a run on purpose?

## Hint 2

Build texts from pieces: a list of `(letter, length)` pairs, joined as `letter * length`. With lengths up to 15 you get long runs
often. For the bug that survives every round trip, write a plain example test: what must `encode("a" * 12)` be exactly? And
what should `encode("a1")` do?

```
texts  = st.text(alphabet="abc", max_size=30)
runny  = st.lists(st.tuples(st.sampled_from("xyz"), st.integers(1, 15)), max_size=5).map(join pieces)
@given(texts)  round trip        @given(runny)  round trip
def test_exact(): encode("a" * 12) == "a12"; encode("aaabcc") == "a3b1c2"
def test_bad(): with pytest.raises(ValueError): encode("a1")
```
