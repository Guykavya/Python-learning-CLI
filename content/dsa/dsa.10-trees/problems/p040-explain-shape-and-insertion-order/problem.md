# Explain: the shape depends on the insertion order

Chapter section 9 inserts the same keys in two different orders and gets two very different trees: a height of 19 in one order and of 500 in the other. Write a short explanation (8 to 12 sentences) in `answer.md` that answers:

1. Insert the keys `1, 2, 3, 4, 5` into an empty BST in this order, then the same keys in the order `3, 1, 5, 2, 4`. Describe both trees (where is each key?) and give the height of each, counted in nodes.
2. Why does every sorted insertion order give a **chain**? What is the height of the tree for `n` sorted keys?
3. What does that height mean for `search`, `insert` and `delete`, in big-O terms, and why does "a BST makes search `O(log n)`" hold only sometimes?
4. All the trees you built in question 1 have the **same inorder** traversal. What is it, and why does the insertion order not change it?
5. Name one order of insertion that gives the **smallest possible** height for the keys `1` to `7`, and what height that is. How does an ordinary order of random keys compare (use the numbers of the chapter)?
6. What do balanced trees (section 14) change, in one sentence?

Use the chapter (section 9: "Why the order of insertion matters: the shape", and section 14). Then compare with the model answer and rate yourself.
