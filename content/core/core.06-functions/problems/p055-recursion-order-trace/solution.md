## Walkthrough

**down_up(2)** prints `down 2`, then runs the whole of `down_up(1)` (which prints `down 1`, runs
`down_up(0)` printing `bottom`, then prints `up 1`), and only then prints `up 2`. The "down" lines
happen on the way into the recursion, the "up" lines on the way back out, in reverse order.

**tree(2)** runs `tree(1)` (which prints `node 1`, since its two `tree(0)` calls print nothing),
then prints `node 2`, then runs `tree(1)` again (`node 1`).

**build(3)** is `build(2) + [3]`, which is `(build(1) + [2]) + [3]`, which is
`(([] + [1]) + [2]) + [3]` = `[1, 2, 3]`. The list is assembled on the way back up.

## The exact output

```text
down 2
down 1
bottom
up 1
up 2
node 1
node 2
node 1
[1, 2, 3]
```
