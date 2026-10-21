# Every other word

Read one line of at least one word. Print five lines using slices:

```
Even positions: <words at index 0, 2, 4, ...>
Odd positions: <words at index 1, 3, 5, ...>
Reversed: <all words, last first>
Last three: <the last three words, or all of them if there are fewer>
Without ends: <all words except the first and the last>
```

Separate words with single spaces. If a slice is empty, the line ends right after the colon,
like `Odd positions:`.

**Example**

Input:
```
a b c d e f g
```
Output:
```
Even positions: a c e g
Odd positions: b d f
Reversed: g f e d c b a
Last three: e f g
Without ends: b c d e f
```
