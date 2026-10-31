## Hint 1

How many `calls` variables exist in Neha's program? How many `wrapper` functions? What does
`global` say about which variable `calls += 1` changes?

## Hint 2

Ask "how many times does this line run?" for a line in the body of `count` and for a line in
the body of `wrapper`. Then: the answer to part 3 moves `calls = 0` into `count` and replaces
`global` with `nonlocal`.
