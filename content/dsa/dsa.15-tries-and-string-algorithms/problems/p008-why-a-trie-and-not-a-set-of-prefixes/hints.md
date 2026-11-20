## Hint 1

Ask what `prefix in some_set` really does with a string of length `p`: before it can find the bucket, it needs the hash of the string. How is the hash of a string computed?

## Hint 2

Count the characters in `word[:0], word[:1], ..., word[:L]`. That sum is both the copying work of `insert` and the memory used. Compare with the number of nodes the trie creates for the same word.

## Hint 3

For question 4, look at the operations of chapter sections 6 to 8. Which of them walk **down from a prefix** to the words below it? A set has no "below".
