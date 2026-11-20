# Fix the TLE

The program in `starter.py` is **correct but too slow** on big inputs. Change its data structures and its input/output, but not what it computes.

The task it solves: a queue of integers. Operations arrive, one per line:

- `push x`: add `x` at the back.
- `pop`: remove the front element and print it; if the queue is empty print `empty`.
- `size`: print the current number of elements.

## Input

The first line holds `q` (`1 <= q <= 4 * 10**5`); then `q` operation lines.

## Output

One line for every `pop` and every `size`, in order.

## Example

```text
6
push 5
push 7
pop
size
pop
pop
```
```text
5
1
7
empty
```

## What the tests check

On a large input the tests measure:

- the number of `input()` calls (at most 1000),
- the number of writes to standard output (at most 1000),
- the total time (at most 3 seconds).

The slow program loses on all three. There are three separate problems in it; find them with the timing ideas of chapter sections 3 to 5.
