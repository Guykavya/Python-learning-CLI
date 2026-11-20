## Hint 1

Ask the questions of chapter section 22, in this order:

1. Must every solution be **listed**? Then the work is at least the size of the output: backtracking.
2. Is there a local choice that is **provably** safe (an exchange argument)? Then greedy.
3. Otherwise: do different choice sequences reach the **same small state**? Then DP.

## Hint 2

For any greedy idea, look for a small counterexample before trusting it. Coin systems: try amounts below 10 with `[1, 3, 4]`. Knapsack: try two items where the best ratio item is heavy and blocks a better pair. If you cannot find one, try to prove the rule by swapping one choice of an optimal answer for the greedy choice.

## Hint 3

Tasks 5 and 6 differ by one word, "fraction", and task 8 has a twin. The point of those pairs is that a tiny change in the question changes the tool. For each pair, say exactly which property is lost or gained (the exchange argument; the need to list).
