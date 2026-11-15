## Hint 1

Keys by length: pear 4, fig 3, apple 5, kiwi 4, date 4, plum 4. Four words have key 4; stable order keeps pear, kiwi, date, plum.

## Hint 2

`reverse=True` with `key=len`: apple first, then the four 4-letter words **in input order**, then fig. Compare with the tuple key `(-len(w), w)` which sorts ties alphabetically.

## Hint 3

Last letters: pear r, fig g, apple e, kiwi i, date e, plum m. Sorted by letter: e (apple, date), g, i, m, r. `sorted(nums, key=abs)` orders by absolute value: -1, 2, 3, -4.
