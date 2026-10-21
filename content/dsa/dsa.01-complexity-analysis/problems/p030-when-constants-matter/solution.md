The model answer is shown when you check. The ideas that must appear:

1. Python loops pay interpreter overhead every pass; built-ins like `sum` loop in C. Same O(n), about 10x apart.
2. `log2(10^6)` is about 20 and grows very slowly; the sort runs in optimised C, so O(n log n) is close to O(n) here.
3. For 5 items, constants and overheads decide; Big-O is about growth for large `n`.
4. Choose by Big-O first. A worse growth rate loses by factors like 10^4 at contest sizes, far beyond any constant.
   Use constant factors (measured) only among equal Big-O or for small inputs.
5. Speed-ups without a new algorithm: built-ins, reading input in one go, one join for output, hoisting work out
   of loops.
