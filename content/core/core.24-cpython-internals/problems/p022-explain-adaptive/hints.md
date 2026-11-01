## Hint 1

Compare the three listings line by line. Which lines changed, and which did not? For each changed
name, ask: what does the new name promise about the operands? What would the generic
instruction have to do at every execution that the new one can skip? Where could the interpreter
store "what types I saw last time" so that it is next to the instruction?

## Hint 2

Shape of a good answer:

```
1. generic op checks types every time -> after warm-up, replaced in place by a specialised op
   that ASSUMES the types (guard + fast path); data lives in inline CACHE entries
2. guard fails -> falls back to the generic behaviour (still correct), counts misses,
   later re-specialises (ADD_FLOAT); cost = failed guards + slow path; unstable types never settle
3. benefit: same types every iteration (ints in a loop, one class's attribute)
   little benefit: mixed types; time spent in C functions
4. dis.dis(f, adaptive=True) after calling f; names/warm-up are version details;
   not a JIT: still bytecode, no machine code (the 3.13+ JIT is separate)
```
