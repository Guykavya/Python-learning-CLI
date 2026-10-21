See the model answer shown when you check. The ideas that must appear:


1. List `in` compares with each item from the start: O(n).
2. Inside a loop of n names it adds up to about n²/2 comparisons: roughly 20 billion for 200,000.
3. Set `in` hashes the name and jumps to a slot: O(1) on average, so the loop is O(n).
4. A set has no order and no duplicates, needs hashable items, and uses more memory.
5. A list is better when you need order, positions or duplicates, or for a handful of items.
