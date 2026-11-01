## Hint 1

Read each instruction as "what does it pop, what does it push?". Where does a value go when
`STORE_FAST` takes it off the stack, and how does `dis` know to print the name `result` for the
argument `2`? What could make an interpreter faster: fewer instructions, or faster ones?

## Hint 2

A good answer has this shape:

```
1. line number (only on first instr of a line) | opname | oparg (meaning per opcode) | decoded arg
2. table: [3, 4] -> [12] -> [] -> [12] -> [12, 1] -> [13] -> returned
   result lives in local slot 2 of the frame (index into co_varnames)
3. fewer dispatches for common pairs; borrow = no refcount change; small int in the argument
4. bytecode is an implementation detail -> test co_* attributes or behaviour, not listings
```
