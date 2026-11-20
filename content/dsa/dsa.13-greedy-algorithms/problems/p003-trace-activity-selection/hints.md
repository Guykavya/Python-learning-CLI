## Hint 1

Sort by end time and write the list down before you trace anything. Ends: `(5,9)` 9, `(1,4)` 4, `(3,5)` 5, `(0,6)` 6, `(4,7)` 7, `(6,9)` 9, `(8,11)` 11, `(11,12)` 12. Two events end at 9: the start time breaks the tie, so `(5, 9)` comes before `(6, 9)`.

## Hint 2

The first event always fits, because every start is `>= -inf`. After that, ask only one question per line: "is `s >= last_end`?" `(4, 7)` starts at 4 and `last_end` is 4: is `4 >= 4`? `(11, 12)` starts at 11; what is `last_end` at that moment?

## Hint 3

On a `take` line the code sets `last_end = e` and **then** prints, so the printed value is the new end. On a `skip` line the printed value is the unchanged one. The last line prints the count and the list of chosen events in the order they were taken.
