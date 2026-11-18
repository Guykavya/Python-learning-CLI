## Approach

Turn "the notebook saves time" into a count. First count how often each state is asked without the notebook (the repeats), then argue that with the notebook each state is worked out exactly once, so the cost is the number of states times the work per state. Then test the idea on two recursions where it fails or misleads: one with no repeated states (permutations), one whose key does not describe the state (`count_ways`).

## Model answer

See `answer.md`.

## What to check

- You **named** repeated calls with numbers, not "many calls repeat".
- You said **which** property the notebook exploits (overlapping sub-problems).
- You linked the running time to the **number of distinct states**, not to the number of calls.
- You explained why `perms` gets nothing from a cache: its states never repeat.
- You named both bugs of `count_ways`: a key that does not identify the state, and a shared default dictionary.

## Another way

Think of the states as the nodes of a graph, with an arrow from each state to the smaller states it needs (chapter section 1: every DP is a walk over a DAG). Plain recursion walks every **path** through that graph, and the number of paths can be exponential. The notebook makes it visit every **node** once. For `fib`, the graph has `n + 1` nodes but about `1.6**n` paths. For `perms`, the "graph" is already a tree: every node has exactly one path to it, so there is nothing to save.
