## Hint 1

Run the starter with the example input. Fix the first crash, run again, and repeat. Then compare each output line with the specification character by character.

## Hint 2

Check each line: How does `split(" ")` treat double spaces? Is `words[1]` the last word? Is the result of `lower()` stored? Which slice gives the last two characters? Can you `+` a string and a number?

## Hint 3

The bugs: `split(" ")` instead of `split()`; `words[1]` instead of `words[-1]`; `first.lower()` result thrown away, and the initial not lowercased; `year[:-2]` instead of `year[-2:]` with the year not stripped; greeting built from the raw name instead of the cleaned words; `"..." + 2026 - int(year)` mixes str and int.
