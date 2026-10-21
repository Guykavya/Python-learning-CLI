See the model answer shown when you check. The ideas that must appear:


1. `[0] * 3` holds three references to the int 0; ints are immutable, and assignment replaces a reference.
2. The outer `* 3` holds three references to one row list (diagram).
3. `board[1][1] = 5` changes slot 1 of that one shared row, which every slot of `board` refers to.
4. `board[0] is board[1]` is `True`.
5. `[[0] * 3 for _ in range(3)]`, or a loop that appends `[0] * 3` each time: a new row every time.
6. `[[]] * 3` or `[{}] * 3`.
