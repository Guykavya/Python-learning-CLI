# Search with an inverted index

Read `n` documents, one per line (document numbers start at 1). Words are separated by spaces
and compared in lowercase. Build an **inverted index**: a dict from each word to the set of
document numbers containing it.

Then read `q` queries:

| Query | Meaning |
|---|---|
| `and W1 W2 ...` | documents containing **all** the words |
| `or W1 W2 ...` | documents containing **any** of the words |
| `not W1 W2` | documents containing W1 but **not** W2 |

Print the matching document numbers in increasing order separated by spaces, or `none`.

**Example**

Input:
```
3
The cat sat
the dog sat down
A cat and a dog
4
and cat dog
or cat down
not sat cat
and fish cat
```
Output:
```
3
1 2 3
2
none
```
