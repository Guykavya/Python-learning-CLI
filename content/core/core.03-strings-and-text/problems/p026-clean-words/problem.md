# Clean words for counting

Before counting words, text must be cleaned. Read a line and:

1. remove every ASCII punctuation character (those in `string.punctuation`),
2. casefold it,
3. split it into words.

Print:

```
Words: <number of words>
<the cleaned words joined by single spaces>
```

**Example**

Input:
```
Hello, world! "Hello" again... don't STOP.
```
Output:
```
Words: 6
hello world hello again dont stop
```

Note that `don't` becomes `dont`: the apostrophe is punctuation. Text that is only punctuation has 0 words and an empty second line.
