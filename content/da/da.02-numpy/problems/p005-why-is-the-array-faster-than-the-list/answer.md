## Model answer

1. **Memory.** A Python list holds **pointers to objects**: each item is an address of a full Python integer object (about 28 bytes plus the 8-byte pointer), scattered around memory. A NumPy array holds the raw numbers themselves, all of **one type** (`int64`, 8 bytes each), side by side in **one contiguous block**. The array knows its dtype once, for all elements.

2. **Work per step.** For `total += v * v` the interpreter must follow the pointer, check the type of `v` (int? float? something with its own `__mul__`?), find the right multiply, create a new integer object for the product, check types again for the addition, create another object for `total`, and drop the old ones. That is dozens of machine steps of bookkeeping for one multiply. NumPy checks the dtype **once**, then the **loop runs in C** over the block: load 8 bytes, multiply, add, move 8 bytes on. There are **no per-element type checks** and no objects created, and the CPU can read the contiguous block quickly from its cache (and often process several numbers per instruction).

3. **When it is not faster.** Calling a NumPy function has a fixed overhead (checking arguments, making the result array). For a handful of elements that overhead is larger than a short Python loop. NumPy wins when arrays are large (hundreds of elements or more), and only when the loop stays inside NumPy: `for v in arr:` is even slower than a list loop, because each element becomes a NumPy scalar object.

**Checklist: your answer should mention**
- [ ] a list stores pointers to objects; an array stores the raw values
- [ ] one type (dtype) for the whole array
- [ ] one contiguous block of memory
- [ ] the loop runs in C (compiled code), not in the interpreter
- [ ] no per-element type checks or object creation
- [ ] small arrays: the call overhead can make NumPy slower
