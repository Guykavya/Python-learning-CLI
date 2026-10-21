# Simulate a growing list

A Python list keeps its items in a block of memory with room for a fixed number of items (its **capacity**).
When the block is full and you append, a bigger block is reserved and every item is **copied** across.

This program simulates the simplest version of that rule: when full, double the capacity. It counts how many
item copies all the growing costs. Predict **exactly** what it prints. Do not run it.

```python
capacity = 1
size = 0
copies = 0
for item in range(1, 18):
    if size == capacity:
        copies += size
        capacity = capacity * 2
        print("grow before item", item, "copy", size, "capacity", capacity)
    size += 1
print("items", size, "copies", copies, "capacity", capacity)
```

Write your answer in `answer.txt`, one line per printed line.

## After you answer

17 appends caused how many copies in total? Compare that number with the number of items.
If you appended 1000 items, roughly how many copies would there be? What does that say about the average cost
of one append?
