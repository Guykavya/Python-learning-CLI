# Greedy word wrap

Read a width `W` (a whole number, at least 1) and then one line of text. Print the words
wrapped into lines of at most `W` characters:

- Words on a line are separated by one space.
- Fill each line with as many words as fit, in order, then start a new line ("greedy").
- A word longer than `W` goes on a line of its own (do not cut it).

Finally print `Lines: N`.

**Example**

Input:
```
12
the quick brown fox jumps over the lazy dog
```
Output:
```
the quick
brown fox
jumps over
the lazy dog
Lines: 4
```

If the text has no words, print only `Lines: 0`.
