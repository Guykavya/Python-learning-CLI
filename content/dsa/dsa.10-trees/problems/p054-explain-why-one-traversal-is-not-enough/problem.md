# Explain: why one traversal is not enough

Chapter section 11 starts with the question: "Is a tree determined by its preorder list?" Write an explanation (10 to 14 sentences) in `answer.md` that answers:

1. Give **two different trees** that have the **same preorder** `[1, 2, 3]`. Write each tree as a level-order list (`None` for a gap, as in `build`). Then give a third tree with the same preorder.
2. What information does a preorder list lose? Say it in your own words (hint: what happens at the end of the left subtree?).
3. Name **two different kinds of extra information** that make the tree unique again, and show on the pair `[1, 2]` and `[1, None, 2]` what each one looks like (the inorder list for one; the text of the other).
4. A BST needs only **one** traversal. Why? Which rule replaces the extra information?
5. The preorder + inorder method needs **distinct values**. Give an example with a repeated value in which two different trees have the same preorder **and** the same inorder.
6. In `serialize` from section 11, why does the text of every tree contain exactly `2n + 1` tokens for `n` nodes?

This problem is **self-rated**: nothing checks your text by machine. Use the chapter (section 11), then compare with the model answer and rate yourself.
