- **Comparing the original text.** `"Jon  Smith"` (two spaces) and `"JOHN SMITH"` score lower than they should.
  Normalise first.
- **`for j in range(len(keys))` inside `for i`.** That compares a name with itself (ratio 1) and every pair twice.
- **`>` instead of `>=`.** A pair exactly at the threshold is included.
- **Normalising inside the double loop.** It repeats the same work 300 times per name.
- **Returning the names, or the ratios.** The task returns sorted `(i, j)` position tuples.
- **Treating the result as a decision.** A high ratio means "have a look"; `Priya Nair` and `Priya Nayar` may be two
  people. Never delete on a similarity score alone.
- **Sorting the pairs by ratio.** They must be sorted by position.
