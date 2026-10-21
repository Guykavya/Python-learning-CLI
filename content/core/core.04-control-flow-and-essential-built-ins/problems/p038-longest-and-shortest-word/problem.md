# Longest and shortest word

Read a line of words. Print:

```
Longest: <word> (<n> letters)
Shortest: <word> (<n> letters)
```

When several words have the same length, report the one that comes **first**. If there are
no words, print `No words`.

**Example**

Input `the quick brown fox jumps`. Output:

```
Longest: quick (5 letters)
Shortest: the (3 letters)
```

Use `max` and `min` with `key=`. The tests check this. Write `1 letter` for a one-letter word.
