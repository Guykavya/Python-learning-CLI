# Explain: read a bytecode listing

CPython's virtual machine is a **stack machine**: most instructions take their inputs from the
top of a value stack and push their result back. `dis.dis(func)` prints a function's bytecode.
Here is a small function and its listing.

```python
def area(width, height):
    result = width * height
    return result + 1
```

Output of `dis.dis(area)` on **Python 3.14** (other versions print different instruction names;
the ideas are the same):

```
  1           RESUME                   0

  2           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (width, height)
              BINARY_OP                5 (*)
              STORE_FAST               2 (result)

  3           LOAD_FAST_BORROW         2 (result)
              LOAD_SMALL_INT           1
              BINARY_OP                0 (+)
              RETURN_VALUE
```

For reference, `area.__code__.co_varnames` is `('width', 'height', 'result')`.

Write `answer.md` (about 250 to 350 words) that answers these four questions:

1. **Columns.** What do the first column (`1`, `2`, `3`), the instruction name, the number after
   it and the text in brackets mean? Why do some lines have no number in the first column?
2. **The stack, step by step.** For the call `area(3, 4)`, write the value stack after each
   instruction from `LOAD_FAST_BORROW_LOAD_FAST_BORROW` to `RETURN_VALUE`. Say which
   instructions pop, which push, and where `result` lives when it is not on the stack.
3. **Odd names.** `LOAD_FAST_BORROW_LOAD_FAST_BORROW` loads two variables in one instruction, and
   `LOAD_SMALL_INT` pushes `1` without looking in `co_consts`. Why would the interpreter
   designers add such instructions? (One or two sentences each.)
4. **Versions.** Python 3.11 shows `LOAD_FAST`, `LOAD_FAST`, `LOAD_CONST` in places where 3.14 shows
   the instructions above. What does that tell you about writing tests or tools that depend on
   exact `dis` output, and what should such a tool look at instead?

**Example of the level of detail expected (a different instruction)**

> `STORE_FAST 2 (result)` pops the top of the stack and writes it into local slot 2 of the
> frame. The `2` is an index into `co_varnames`, and `dis` prints the name it finds there,
> `result`, in brackets so you do not have to look it up.
