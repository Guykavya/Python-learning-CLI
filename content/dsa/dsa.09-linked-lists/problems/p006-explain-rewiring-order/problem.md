# Explain: why does order matter when rewiring?

A classmate wants to insert a new node `99` after `node` in the list `1 -> 2 -> 3` (`node` is the node holding `1`). They write the two lines in this order:

```python
new = ListNode(99)
node.next = new          # line A
new.next = node.next     # line B
```

and their list printer never stops: `1 -> 99 -> 99 -> 99 -> ...`.

Also look at the loop body of the iterative reversal (chapter section 6):

```python
nxt = cur.next     # 1
cur.next = prev    # 2
prev = cur         # 3
cur = nxt          # 4
```

Write a short explanation (8 to 12 sentences) in `answer.md` that answers:

1. After line A, which nodes can no longer be reached, and why does Python not "remember" them for you?
2. What does line B really do after line A, and why does that make a cycle?
3. What is the correct order of the two lines, and what general rule does it follow?
4. In the reversal, why must line 1 come **before** line 2? What would be lost otherwise?
5. Give a simple habit that prevents this whole class of bugs.

Use the chapter (section 2, "Variables are labels, not boxes"; section 3, "Order matters when you rewire"; section 6, "Why `nxt` must be saved first"). Then compare with the model answer and rate yourself.
