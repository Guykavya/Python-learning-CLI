## Approach

One sentence per behaviour, each aimed at a family of bugs:

| Property | Catches |
|---|---|
| idempotent: `norm(norm(t)) == norm(t)` | `only_halves_runs` |
| no edge spaces, no `"  "`, no tab or newline | `no_strip`, `keeps_tabs_and_newlines` |
| `.split()` of output equals `.split()` of input | `changes_the_words` |
| no duplicates, and `dedupe` is idempotent | (guards the basics) |
| `set(out) == set(xs)` | `dedupe_drops_zero` |
| first-appearance positions are increasing | `dedupe_sorts`, `dedupe_keeps_last` |
| output lengths equal the sorted input lengths | `sort_longest_first` |
| equal-length words keep input order (stability) | `sort_not_stable` |

The alphabets matter as much as the properties: with plain `st.text()` almost no example contains a tab or a run of four spaces, and
with `st.integers()` repeats are rare, so the bugs would pass.

## Code

```python
from hypothesis import given, settings, strategies as st

from target import dedupe, normalise_whitespace, sort_by_length

spacey = st.text(alphabet=" \t\nab", max_size=25)
small_ints = st.lists(st.integers(min_value=0, max_value=6), max_size=15)
words = st.lists(st.text(alphabet="abc", max_size=4), max_size=12)


@settings(derandomize=True, database=None, max_examples=100)
@given(spacey)
def test_normalise_is_idempotent(text):
    once = normalise_whitespace(text)
    assert normalise_whitespace(once) == once, "Normalising twice must give the same result as once."


@settings(derandomize=True, database=None, max_examples=100)
@given(spacey)
def test_normalise_output_is_clean(text):
    out = normalise_whitespace(text)
    assert out == out.strip(), "No space at the start or the end."
    assert "  " not in out, "No two spaces in a row."
    assert "\t" not in out and "\n" not in out, "Tabs and newlines must become single spaces."


@settings(derandomize=True, database=None, max_examples=100)
@given(st.text(alphabet=" AbC", max_size=15))
def test_normalise_does_not_change_letters(text):
    assert normalise_whitespace(text).split() == text.split(), "Only whitespace may change, never the words."


@settings(derandomize=True, database=None, max_examples=100)
@given(small_ints)
def test_dedupe_is_idempotent_and_unique(xs):
    out = dedupe(xs)
    assert len(out) == len(set(out)), "No item may appear twice."
    assert dedupe(out) == out, "Deduplicating a deduplicated list changes nothing."


@settings(derandomize=True, database=None, max_examples=100)
@given(small_ints)
def test_dedupe_keeps_all_values_in_first_seen_order(xs):
    out = dedupe(xs)
    assert set(out) == set(xs), "No value may be lost (watch out for 0)."
    positions = [xs.index(x) for x in out]
    assert positions == sorted(positions), "Items must stay in the order they first appeared."


@settings(derandomize=True, database=None, max_examples=100)
@given(words)
def test_sort_by_length_orders_by_length(ws):
    out = sort_by_length(ws)
    assert [len(w) for w in out] == sorted(len(w) for w in ws), "Shortest first, nothing lost."


@settings(derandomize=True, database=None, max_examples=100)
@given(words)
def test_sort_by_length_is_stable(ws):
    out = sort_by_length(ws)
    for n in {len(w) for w in ws}:
        assert [w for w in out if len(w) == n] == [w for w in ws if len(w) == n], (
            "Words of equal length must keep the order they had in the input.")
```

## Cost

Eight tests, at most 100 small examples each: a second or two.

## Another way

An oracle: `dedupe(xs) == list(dict.fromkeys(xs))`. It is shorter and catches all three dedupe bugs, but it is only a good test
if you trust the oracle more than the code (see p037).
