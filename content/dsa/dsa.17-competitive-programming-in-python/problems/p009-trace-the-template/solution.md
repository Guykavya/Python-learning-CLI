## Approach

Run the program in your head with two lists: what has been **printed** and what is waiting in `out`.

| Step | Printed so far | `out` |
|---|---|---|
| case 1: `solve` prints, returns `9 1` | `solving 3` | `Case 1: 9 1` |
| case 2: `solve` prints, returns `7 0`; then `two done` | `solving 3`, `solving 1`, `two done` | `Case 1`, `Case 2` |
| case 3: `solve` prints, returns `8 2` | ... `solving 4` | three entries |
| after the loop: one write of `out` | the three `Case` lines | |
| last statement in `main` | `end` | |

Final output:

```text
solving 3
solving 1
two done
solving 4
Case 1: 9 1
Case 2: 7 0
Case 3: 8 2
end
```

The program was run with this input to check the result.

## Why it matters

In a contest your debug prints go to the same stream as the answer. Collecting answers in `out` and writing them at the end means every debug line appears **before** the answers, mixed with nothing. On a judge such debug lines would make the output wrong; print them to `sys.stderr` instead.

## Complexity

`O(total n)`.

## Another way

Check by running the program with `python3 template.py < input.txt`, but only after you have written your prediction.
