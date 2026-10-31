## Hint 1

`text` has three lines: `Apple pie`, `banana split`, `Cherry tart`. Without `re.M`, `^` can only
be at index 0 and `$` only at the very end. With `re.M`, list the start and end of each line and
ask what `\w+` can take from there.

## Hint 2

`^[a-z]` needs a **lower-case** first letter. Which lines start with one? What changes when
`re.I` is added? For `.`: does it cross the `\n` between `pie` and `banana` without `re.S`?

## Hint 3

`é` and `ï` are letters, so normally `\w` matches them. With `re.ASCII`, `\w` is only
`[a-zA-Z0-9_]`, so the words break apart at those letters. What pieces are left of `café` and
`naïve`?
