## Approach

Prove the two directions separately. The direction "odd cycle, so not bipartite" only needs the alternating walk around the cycle. The direction "no odd cycle, so bipartite" needs a colouring that you can actually build: BFS layers coloured by parity. Then the only thing to check is which edges can go wrong, and the BFS layer fact (an edge changes the distance by at most one) reduces that to edges inside one layer, which close odd cycles.

Draw it: a 5-cycle `0-1-2-3-4-0` with BFS from 0 has layers `{0}`, `{1, 4}`, `{2, 3}`. The edge `2-3` lies inside layer 2. The tree paths from 2 and 3 meet at 0 (layer 0), and the cycle `0-1-2-3-4-0` has `2 * (2 - 0) + 1 = 5` edges.

## Model answer

See `answer.md`.

## What to check

- You proved **both** directions, not only "odd cycle, so impossible".
- You used the fact that an edge joins layers at most one apart, and said **why** (distance changes by at most one per step, in both directions).
- Your cycle length in question 4 is `2(k - j) + 1`, and you said why the two tree paths do not overlap (they meet first at `a`).
- In question 5 you connected the proof to the algorithm: the BFS colouring **is** the parity colouring.
- In question 7 you named the real difference: forced choices against branching choices.

## Another way to see it

Think of the colour as "even or odd number of steps from `s`". Two different walks from `s` to the same vertex have lengths with the same parity in a bipartite graph. If some vertex can be reached by both an even and an odd walk, then going out by one and back by the other is a closed walk of odd length, and every closed walk of odd length contains an odd cycle.
