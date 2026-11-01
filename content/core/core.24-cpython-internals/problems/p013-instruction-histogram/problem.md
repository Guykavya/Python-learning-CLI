# An instruction histogram

`dis.get_instructions(x)` gives you the bytecode of a function (or of a code object) as a
sequence of `Instruction` objects. Each one has an `opname` such as `"LOAD_FAST"` and an
`argval`. Counting the opnames gives a quick "fingerprint" of a function: lots of `LOAD_...`
instructions, a few jumps, some calls.

One catch: a function defined **inside** another function (or a `lambda`, or a generator
expression) has its own code object. The outer function's bytecode does not contain the
inner one's instructions; it only contains the inner **code object** as a constant, in
`outer.__code__.co_consts`.

Copy `starter.py` to `solution.py` and write two functions.

**`opcode_histogram(obj, recursive=False)`** takes a function or a code object and returns a
`collections.Counter` that maps each opname to how many times it appears in
`dis.get_instructions(obj)` (use the default arguments of `get_instructions`). With
`recursive=True`, also add the instructions of every code object found in `co_consts`, and in
their `co_consts`, at any depth.

**`by_prefix(hist)`** takes such a Counter and returns a new `Counter` keyed by the part of
each opname before the first underscore (the whole name if it has no underscore).
`"LOAD_FAST"` and `"LOAD_CONST"` both count towards `"LOAD"`; `"RESUME"` stays `"RESUME"`.

**Version warning.** The exact opnames and their counts change between Python versions
(3.13 and 3.14 merge pairs of loads into one instruction, 3.14 renamed several). So never
compare against one fixed listing. What *is* stable: every function loads something, every
loop jumps backwards, and the outer/inner split of code objects.

**Example**

```python
def area(w, h):
    return w * h

hist = opcode_histogram(area)
hist                    # Python 3.14 (other versions differ):
                        # Counter({'RESUME': 1, 'LOAD_FAST_BORROW_LOAD_FAST_BORROW': 1,
                        #          'BINARY_OP': 1, 'RETURN_VALUE': 1})
hist.total() == len(list(dis.get_instructions(area)))    # True on every version

by_prefix(Counter({"LOAD_FAST": 3, "LOAD_CONST": 1, "RETURN_VALUE": 1}))
# Counter({'LOAD': 4, 'RETURN': 1})

def outer():
    def inner(x):
        return x + 1
    return inner

opcode_histogram(outer).total()                  # only outer's own instructions
opcode_histogram(outer, recursive=True).total()  # outer's + inner's
```
