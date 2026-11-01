# Explain: pickling, the main guard and start methods

A teammate wrote this and it crashes:

```python
from multiprocessing import Pool

with Pool(4) as pool:
    print(pool.map(lambda x: x * 2, [1, 2, 3]))
```

On their Linux laptop with Python 3.14 (inside a guard) it ends with:

```text
_pickle.PicklingError: Can't pickle <function <lambda> at 0x7c2721ae6090>: it's not found as __main__.<lambda>
```

(The address is machine-specific.) Without the guard, on Windows, it fails differently, with a
`RuntimeError` about "the bootstrapping phase".

Write `answer.md` (about 300 to 450 words) that explains:

1. **Why the lambda fails**: how a function is sent to a worker process, and what that means
   for lambdas, nested functions and methods of local classes.
2. **What must be picklable** in a process pool call: name at least four things that cross the
   process boundary.
3. **Why the `if __name__ == "__main__":` guard** is needed, and what happens without it.
4. **The three start methods**, `spawn`, `fork` and `forkserver`: what each does, which is the
   default where (Windows, macOS, Linux in Python 3.14), and one danger of `fork`.
5. **Why processes cost more than threads**, with at least two concrete costs, and what that
   means for small tasks.
6. **The fixed version** of the snippet.

**Example of the level of detail expected (a different question)**

> *"Why can't I pass an open file to a worker?"* A file object wraps an OS file descriptor that
> belongs to the parent process, so `pickle` refuses it (`TypeError: cannot pickle
> '_io.TextIOWrapper' object`). Pass the **path** instead and let the worker open the file
> itself.
