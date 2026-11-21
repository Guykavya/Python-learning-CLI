## Approach

The model answer is in `answer.md`. The method of the chapter (15.5): **choose from the business**. Money, inventory, unique usernames and business limits want **C** (an error is better than selling the last seat twice or letting a user hold a 4th task); shopping carts, likes, presence and feeds often prefer **A**. Say what the user *sees*; a technical choice is only complete when you can describe the screen.

## Cost

Nothing to build. The cost of getting it wrong shows up as a lost update with no error, or as a feature that goes dark when one network link fails.

## Another way

Run the chapter's two-mode store (a 3-node store split into {A, B} and {C}, CP versus AP) on your machine: in CP the write at C is refused; in AP both writes are accepted and last-write-wins silently discards one. Seeing the lost update once makes the conflict-handling question concrete.
