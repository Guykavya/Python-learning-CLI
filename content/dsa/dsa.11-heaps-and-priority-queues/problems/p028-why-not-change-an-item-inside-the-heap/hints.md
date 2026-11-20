## Hint 1

Run the program and look at the three printed lines. Draw the heap `[1, 3, 2, 0, 5, 4, 7]` as a tree: index 0 is the root, the children of index `i` are `2i + 1` and `2i + 2`. Go through each parent and its two children. Where is a child **smaller** than its parent?

## Hint 2

`heappop` takes `heap[0]`, moves the last item to the root and lets it sink along **one path**. Which positions of the list does it read? Does it ever read index 3 before it reaches it through the path? What would it need to know about the whole list to detect that `0` is smaller than the root `1`?

## Hint 3

For the two correct ways, think about what you do to the **old** entry. Either you leave it (and remember that it is dead), or you change it and then fix the heap. Fixing the whole heap costs `O(n)`; fixing one position costs `O(log n)` but needs its index. What data structure answers "at which index is this item?" in `O(1)`?
