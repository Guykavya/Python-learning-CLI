**1. Columns.** The first column is the source line number. It is printed only on the first
instruction that belongs to a new line, so the blank cells mean "still line 2" or "still line 3".
Next is the opcode name, then its argument (`oparg`), a small integer whose meaning depends on the
opcode: an index into `co_varnames` for `STORE_FAST`, the operator number for `BINARY_OP`, the
value itself for `LOAD_SMALL_INT`. The text in brackets is `dis` being helpful: it decodes the
argument into a name, an operator symbol or a constant. `RESUME 0` is bookkeeping at function
start (tracing, interrupt checks) and touches no values.

**2. Stack for `area(3, 4)`** (top of the stack on the right):

| Instruction | Stack after |
|---|---|
| `LOAD_FAST_BORROW_LOAD_FAST_BORROW (width, height)` | `[3, 4]` (two pushes) |
| `BINARY_OP 5 (*)` | `[12]` (pops 4 and 3, pushes 12) |
| `STORE_FAST 2 (result)` | `[]` (pops 12 into local slot 2) |
| `LOAD_FAST_BORROW 2 (result)` | `[12]` |
| `LOAD_SMALL_INT 1` | `[12, 1]` |
| `BINARY_OP 0 (+)` | `[13]` |
| `RETURN_VALUE` | pops 13 and hands it to the caller |

When it is not on the stack, `result` lives in the frame's array of local variables, slot 2,
next to `width` (slot 0) and `height` (slot 1). Locals are found by index, not by name, which is
why local variables are fast.

**3. Odd names.** Each instruction costs a trip round the evaluation loop (fetch, decode,
dispatch). A *superinstruction* that does two common loads at once halves that overhead for a
very frequent pair. "Borrow" means it pushes the value without increasing its reference count,
which is safe because the local variable keeps the object alive. `LOAD_SMALL_INT` puts the number
directly in the argument, so no constant table lookup is needed and small ints, which are
pre-built objects, are fetched in one step.

**4. Versions.** Bytecode is an implementation detail of CPython: names, counts and order change
in every minor release (3.11 had none of these three instructions). A test that compares a
`dis` listing as text will break on the next version and does not even exist on PyPy. Tools
should look at stable facts instead: code object attributes like `co_varnames`, `co_names`,
`co_argcount`, or the *behaviour* of the function.
