# Print with sep and end

Read three words, each on its own line. Then print them in four different ways,
using the `sep` and `end` parameters of `print()` instead of gluing strings together with `+`.

1. Joined by a dash: `red-green-blue`
2. Joined with nothing between them: `redgreenblue`
3. Joined by a comma and a space, with an exclamation mark at the end: `red, green, blue!`
4. The first word, then the text ` and ` produced by `end`, then the third word on the same line: `red and blue`

Use `input()` without a prompt.

**Example**

Input:
```
red
green
blue
```
Output:
```
red-green-blue
redgreenblue
red, green, blue!
red and blue
```

**Rule:** your program must use the `sep=` keyword at least once and the `end=` keyword at least once.
