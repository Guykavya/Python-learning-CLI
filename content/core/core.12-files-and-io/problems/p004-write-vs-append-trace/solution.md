## Approach

The file after the first block is `one\ntwo\n`, after the append `one\ntwo\nthree\n`, so the first print shows the three lines as a list. The second `"w"` block wipes it and writes `four`. Appending `!!` makes `four!!`, and `write` returns the number of characters written: 2. Reading: `read(2)` gives `fo`, the next `readline()` gives the rest `ur!!` (no newline in the file), the next `readline()` gives an empty string, which `print` shows as an empty line. At the end of the file `read()` gives `""`, so the comparison prints `True`.

## Output

```text
['one', 'two', 'three']
2
fo
ur!!

True
```

## Complexity

O(1).

## Another way

Delete `demo.txt` and change the second block to mode `"w"` instead of `"a"`. Predict again: the first print then shows only `['three']`.
