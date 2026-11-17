# Explain: what does each call return?

Chapter section 3 says that every recursive tree function starts from one sentence: "`f(node)` returns ___ for the tree that starts at `node`." Here are four functions:

```python
def size(node):
    if node is None:
        return 0
    return 1 + size(node.left) + size(node.right)

def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))

def is_leaf(node):
    return node is not None and node.left is None and node.right is None

def count_leaves(node):
    if node is None:
        return 0
    if is_leaf(node):
        return 1
    return count_leaves(node.left) + count_leaves(node.right)
```

Write a short explanation (8 to 12 sentences) in `answer.md` that answers:

1. Finish the sentence "`f(node)` returns ___ for the tree that starts at `node`" for `size`, `height` and `count_leaves`.
2. What does each of the four functions return for `None`, and why is that the right value in each case? In particular, why is `is_leaf(None)` `False` and not `True`?
3. What does each function return for a tree with a single node, and which lines of the code produce that answer?
4. Somebody deletes the `is_leaf` case from `count_leaves`. What does the function return for **every** tree, and why?
5. A new function `max_value(node)` should return the largest value in a tree. Why can it not return `0` for `None`? What should it return instead, and what must the code do with that answer?
6. State in one sentence how you choose the value for the base case `None`.

Use the chapter (section 3, "The one question" and "More examples with the same shape"). Then compare with the model answer and rate yourself.
