## Hint 1

Anagrams have something in common that you can use as a dict key. What do you get if you sort
the letters of `listen` and of `silent`?

## Hint 2

`"".join(sorted(word))` gives `eilnst` for both. Use that as the key and a list of words as the value.

## Hint 3

Before appending, check `if word not in groups[key]` (groups are small), or keep a separate
`seen` set of words.
