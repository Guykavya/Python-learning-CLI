## Hint 1

Take three nodes `1, 2, 3` listed in preorder. Draw all the shapes that you can make with the visiting order node, left, right giving `1, 2, 3`: for example `2` could be the left child of `1` and `3` the right child; or `2` and `3` could both lie on the left. How many shapes do you find? (For three nodes there are five.)

## Hint 2

For question 3: the inorder lists of `[1, 2]` (2 is the left child) and `[1, None, 2]` (2 is the right child) are different; the preorders are equal. And with markers for the missing children, the text of the first tree is `1,2,#,#,#` and of the second `1,#,2,#,#`. For question 5, try two nodes with the same value `1`.
