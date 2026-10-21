**When it runs.** A `for` or `while` loop's `else` block runs once, after the loop, if the
loop ended **normally**: a `for` loop ran out of items, or a `while` condition became false.
The only normal way to skip it is `break`. (An error or leaving the program also skips it.)
A good name for it in your head is **nobreak**.

```python
for n in [1, 2, 3]:
    pass
else:
    print("runs: no break")       # printed

for n in [1, 2, 3]:
    if n == 2:
        break
else:
    print("skipped")              # not printed
```

**Zero iterations and continue.** A loop over an empty string never hits `break`, so its
`else` runs. `continue` only ends one iteration, so it does not affect the `else` either.
The classmate is half right: the `else` does run when the loop never started, but it also
runs after a full normal run.

**What it is for.** Searching. The loop looks at each item and `break`s when it finds what
it wants. If it gets to the end without breaking, nothing was found, and the `else` says so:

```python
for ch in word:
    if ch in "aeiou":
        print("first vowel:", ch)
        break
else:
    print("no vowels")
```

**The flag version.**

```python
found = False
for ch in word:
    if ch in "aeiou":
        found = True
        break
if not found:
    print("no vowels")
```

Both are correct. The `else` version is shorter and cannot forget to set or reset a flag.
The flag version is clearer to readers who do not know the rule, and the flag can be used
again later in the program.

**How it misleads.** Because it looks like `if`/`else`, readers may think it pairs with the
`if` inside the loop, or that it means "if the loop did not run". Keep loops with an `else`
short, line the `else` up exactly with `for`, and add a comment such as `# no break` or
`# not found`.

Key ideas to check: runs when no break; break is the only thing that skips it; runs for empty
loops and with continue; designed for search; flag equivalent; readability tip.
