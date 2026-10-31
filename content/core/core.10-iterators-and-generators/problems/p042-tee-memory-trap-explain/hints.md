## Hint 1

The source can be read only once, but two iterators want every item. Something must remember the
items one iterator has seen and the other has not seen yet. How many items must it remember?

## Hint 2

Compare the **distance** between the two iterators in the two programs. With `sum(big_a)` first,
how far ahead does `big_a` get? With `zip`, how far ahead can one get?

## Hint 3

Answer in order: buffer, distance decides memory, rule (side by side = cheap, far apart = like a
list), do not touch the original, better design (two fresh sources or one pass).
