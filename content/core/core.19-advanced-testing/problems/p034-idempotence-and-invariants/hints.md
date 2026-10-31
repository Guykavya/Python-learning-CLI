## Hint 1

For `normalise_whitespace`, write down what a clean result looks like in plain words: no space at the ends, no two spaces in a row, no tabs
or newlines, the same words in the same order. Each sentence is a property. Which bug does each one catch?

## Hint 2

For `dedupe`: no item twice, no value lost, the order of first appearances kept. For `sort_by_length`: lengths come out sorted, and among words of
equal length the order from the input is kept. To check "order of first appearances" without copying the implementation,
compare `xs.index(x)` for the output items: those positions must be increasing.

```
spacey  = st.text(alphabet=" \t\nab", max_size=25)      # whitespace is common
ints    = st.lists(st.integers(0, 6), max_size=15)        # repeats are common
words   = st.lists(st.text(alphabet="abc", max_size=4))   # equal lengths are common
stable:  for each length n: [w in out if len(w) == n] == [w in words if len(w) == n]
```
