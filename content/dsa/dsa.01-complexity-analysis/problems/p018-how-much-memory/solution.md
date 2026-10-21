The model answer is shown when you check. The ideas that must appear:

1. A: O(1) space, O(n) time.
2. B: O(n) space for the new list.
3. C: slicing copies; O(n) space at any one time but O(n^2) total time. An index is better.
4. D: O(n^2) space; huge for n = 10^4.
5. E: O(1) space, because the set holds at most 10 values.
6. F: O(n) space for the call stack, one frame per open call.
7. F crashes because Python's default recursion limit is about 1000; the loop in A needs no stack.
