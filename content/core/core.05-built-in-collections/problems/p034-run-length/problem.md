# Run-length encoding

Read one line of tokens. Compress each run of **consecutive** equal tokens into `token*count`
(write just `token` when the count is 1). Print the compressed tokens separated by spaces,
then the number of runs:

```
<compressed>
Runs: <number of runs>
```

For an empty line print `(empty)` and `Runs: 0`.

**Example**

Input:
```
a a b c c c a
```
Output:
```
a*2 b c*3 a
Runs: 4
```

The two groups of `a` are separate runs because they are not next to each other.
