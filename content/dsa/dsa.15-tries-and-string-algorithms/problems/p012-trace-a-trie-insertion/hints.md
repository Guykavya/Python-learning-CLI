## Hint 1

`tea` starts with an empty trie except the root, so it creates the nodes `t`, `te`, `tea`: 3 new nodes, 4 in total with the root. Each of them gets pass count 1, and `tea` gets end count 1.

## Hint 2

`ten` walks `t` and `te`, which exist, and needs one new node for `n`. `te` walks two existing nodes and creates nothing: it only changes counts. Which counts does it change?

## Hint 3

The second `tea` creates nothing. Add up: how many of the four words pass through `t`? Through `te`? Through `tea`?
