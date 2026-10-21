See the model answer shown when you check. The ideas that must appear:


1. A list holds a size and a pointer to a block of references; the objects live elsewhere.
2. Slot i is at a fixed offset from the start of the block.
3. A full block is replaced by a bigger one with spare room (over-allocation); copies are rare,
   so the average cost per append is constant. Amortised means averaged over many operations.
4. Every reference must shift one place: O(n) per call, so n calls cost about n²/2 moves.
5. Append and reverse once at the end, or use `collections.deque`.
