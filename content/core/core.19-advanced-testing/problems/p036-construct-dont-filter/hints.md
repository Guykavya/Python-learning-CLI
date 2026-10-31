## Hint 1

For each rule ask: can I describe a valid value as "a free choice, then a fixed transformation"? An even number is "any number times 2". A sorted list is
"any list, sorted". What are the free choices for a pair `(a, b)` with a gap between 1 and 50? And which argument of `st.lists` is about duplicates?

## Hint 2

`strategy.map(function)` generates a value and then applies the function to it. Remember to shrink the *range* of the free choice: if the final numbers go up to 1000
and you double them, the free choice goes up to 500. `st.tuples(a, b)` generates a tuple of one value from each strategy; you can map the tuple again.

```
even_numbers      = integers(-500, 500).map(lambda n: n * 2)
sorted_lists      = lists(integers(-50, 50), max_size=10).map(sorted)
ordered_pairs     = tuples(integers(-100, 100), integers(1, 50)).map(lambda t: (t[0], t[0] + t[1]))
multiples_of_1000 = integers(-1000, 1000).map(lambda n: n * 1000)
distinct_lists    = lists(integers(-20, 20), min_size=2, max_size=8, unique=True)
```
