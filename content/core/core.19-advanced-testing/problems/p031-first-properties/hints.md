## Hint 1

Finish the sentence "for every list `xs`, ..." in different ways for `reverse`: what stays the same about its output
(length? elements?) and what changes (which element is first?). Do the same for `sorted_copy`: what is true about
neighbours in the output, about the elements as a whole, and about the input list afterwards?

## Hint 2

Ask of each property: which wrong function would still satisfy it? "Reverse twice is the original" is satisfied by a
function that does nothing at all. "Output is ascending" is satisfied by a function that returns `[]`. Pair every property with
another one that closes that gap.

```
reverse:      len(out) == len(xs)     and     out[0] == xs[-1], out[-1] == xs[0]   (xs not empty)
sorted_copy:  all(a <= b for a, b in zip(out, out[1:]))
              Counter(out) == Counter(xs)          # same elements, same counts
              xs == copy_made_before_the_call      # input untouched
```
