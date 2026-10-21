## Hint 1

Decide one structure per question: a set of users; a dict of page counts; a dict from day to a
set of users; a dict of day counts.

## Hint 2

Loyal users are the intersection of every day's user set. Start from one day's set (a copy) and
intersect with the others.

## Hint 3

Top pages: sort `(-count, page)`. Busiest day: sort `(-count, day)` and take the first, or use
a loop.
