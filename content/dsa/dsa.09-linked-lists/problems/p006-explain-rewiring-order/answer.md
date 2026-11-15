## Model answer

A variable or a `next` field holds a **reference** to a node; it is a label, not a copy. Before line A, the only reference to node `2` is `node.next`. Line A overwrites that field with the new node, so node `2` (and node `3`, which is reached only through `2`) is **lost**: no variable and no field refers to it any more, so it cannot be reached, and Python will free it. Python does not keep an "old value" of a field for you.

After line A, `node.next` **is** the new node. So line B, `new.next = node.next`, makes the new node point at **itself**. That is a cycle of length one: the printer goes `1 -> 99 -> 99 -> ...` forever.

The correct order is the reverse: first `new.next = node.next` (the new node takes over the rest of the list, so node `2` now has a second reference), then `node.next = new`. The rule is: **a link may be overwritten only after its old value is saved** somewhere else, in another node's `next` or in a variable.

The reversal follows the same rule. Line 2 overwrites `cur.next`, which is the only way to reach the rest of the list. So line 1 must **save** it in `nxt` first. Without that, after `cur.next = prev` the rest of the list is lost and the loop could only walk backwards into the part already reversed.

A good habit: before every `x.next = ...`, ask "what did `x.next` point to, and who else points to it?" If nobody, save it in a variable first. Drawing the boxes and arrows and numbering the steps makes this visible.

Checklist: your answer should mention
- [ ] a variable or `next` holds a **reference** (a label), not a copy of the node
- [ ] after line A, node `2` and node `3` are **lost**: nothing refers to them
- [ ] after line A, `node.next` is the new node, so line B points the node to itself: a **cycle**
- [ ] the correct order: `new.next = node.next` first, then `node.next = new`
- [ ] the rule: **save** the old `next` before you overwrite it
- [ ] in the reversal, `nxt` saves the rest of the list before `cur.next = prev` overwrites the only link to it
- [ ] a habit: draw the arrows / ask "who else points there?" before each assignment to `next`
