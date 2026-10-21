# Menu-driven calculator

Build the core of this module's project: a calculator that runs until the user quits.

**At the start**, print this menu exactly:

```
Menu:
1) add
2) subtract
3) multiply
4) divide
5) power
?) show this menu
q) quit
```

**Then repeat:** read a choice (strip spaces, ignore capitals).

- `1` to `5`: read two numbers, `a` and `b`, one per line (they may have decimals). Compute
  `a + b`, `a - b`, `a * b`, `a / b` or `a ** b`, and print `Result: <value with 2 decimals>`.
- Choice `4` with `b` equal to 0: print `Cannot divide by zero` instead (this does not count
  as a calculation).
- `?`: print the menu again.
- An empty line: ignore it.
- `q` or `quit`: stop.
- Anything else: print `Unknown choice: <choice>`.

**When the user quits**, print `Done. N calculations.` (or `Done. 1 calculation.` for one),
counting only the results that were printed.

**Example** (after the menu):

Input:
```
1
2
3.5
4
1
0
x
q
```
Output:
```
Result: 5.50
Cannot divide by zero
Unknown choice: x
Done. 1 calculation.
```

You may assume the numbers are valid and the input always ends with `q` or `quit`. Use `match`
for the choice.
