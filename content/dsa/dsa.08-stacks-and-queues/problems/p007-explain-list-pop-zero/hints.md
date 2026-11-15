## Hint 1

Picture the list as numbered boxes in a row: box 0, box 1, box 2, ... After `pop(0)` the list must again start at box 0. What has to happen to every item that was in boxes 1, 2, 3, ...?

## Hint 2

Add up the moves: the first `pop(0)` moves `n - 1` items, the next `n - 2`, ... What is the sum, and what is it in big-O? Then: which `deque` method removes from the left, and why does it not need to move anything?
