# Explain: why not `list.pop(0)` for a queue?

A classmate writes a queue like this and says "it passes all my tests":

```python
queue = []
queue.append(job)        # enqueue
job = queue.pop(0)       # dequeue
```

Write a short explanation (8 to 12 sentences) in `answer.md` that answers:

1. Is the code **correct**? Is the order right?
2. What does `pop(0)` have to do inside the list, and how much does one call cost for a list of `n` items? What do `n` dequeues cost in total?
3. Why is `pop()` from the **end** cheap, while `pop(0)` is not?
4. What should they use instead, which two methods, and what does each cost? Why can that structure do it?
5. When would `pop(0)` be completely fine?

Use the chapter (section 3, "Why not a list?" and "Looking inside: a queue built on a fixed array") and your own measurements if you like. Then compare with the model answer and rate yourself.
