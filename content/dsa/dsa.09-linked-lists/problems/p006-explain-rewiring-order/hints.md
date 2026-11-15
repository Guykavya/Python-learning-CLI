## Hint 1

Draw `1 -> 2 -> 3` with arrows. Line A redraws the arrow out of node `1`. Count the arrows that still lead **into** node `2`. If the count is zero, can any later line ever reach node `2`?

## Hint 2

Right after line A, what is `node.next`? Substitute it into line B: `new.next = ...`. Where does the new node's arrow now go? For the reversal, ask the same question about `cur.next` before and after line 2.
