## Approach

Split the pattern into its named groups and treat each one as a small, separate question:
"which strings can this part match?" Write the smallest and largest value of every numeric range,
and for every optional block say what happens when it is absent. Then run the inputs through it
from left to right and stop at the first character that cannot be matched.

Three ideas carry the whole explanation:

1. Ranges of numbers are written as alternatives of character patterns (`0[1-9]|1[0-2]`),
   because a regex sees characters, not numbers.
2. Nesting optional groups expresses dependence: a fraction only after seconds.
3. A regex checks **shape**. Meaning (does 31 February exist?) is checked in Python code
   afterwards, for example with `datetime`.

The full model answer, with the results of actually running the eight inputs, is in `answer.md`.

## Complexity

Matching is O(n) on the input: every part has a fixed small width and there is no nested
repetition, so there is no risk of catastrophic backtracking.

## Another way

For real code, `datetime.fromisoformat(s)` (Python 3.11+ accepts most ISO-8601 forms) parses and
validates in one call. The regex stays useful when you must **find** timestamps inside longer
text, or when you need the exact pieces as strings.
