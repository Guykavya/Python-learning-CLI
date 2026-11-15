## Hint 1

A key function is called once per element (`n` calls); a comparator is called for every comparison (about `n log n` calls).

## Hint 2

Rock-paper-scissors breaks transitivity: from `rock < paper < scissors` it follows that `rock < scissors`, but the table says the opposite.

## Hint 3

For problem p021 the concatenation order is the same as comparing `a * 10` strings (repeated to a common length), so it comes from a key and a key always gives a valid order.
