## Walkthrough

**First loop.** `"sky"`: no character is a vowel (`y` is not in `"aeiou"`), the inner loop
ends normally, so its `else` prints `'sky' no vowel`. `"tree"`: finds `e`, prints, breaks, the
`else` is skipped. `""`: the inner loop runs zero times, which still counts as ending without
`break`, so `'' no vowel`. `"moon"`: finds `o`.

**While loop.** `count` reaches 3 and the condition becomes false. `count == 5` never
happens, so there was no `break`, and the `else` runs with count 3.

**For with continue.** Prints `i = 0` and `i = 2`. `continue` is not a `break`, so the
`else` runs. `i` is 2 after the loop.

**Last loop.** n: 10, 6, 2, then -2. At -2 the `if` inside the body fires before the
condition is checked again, so it prints and breaks. The `else` is skipped. Then `end -2`.
