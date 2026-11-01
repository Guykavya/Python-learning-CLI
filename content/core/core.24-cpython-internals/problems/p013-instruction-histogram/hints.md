## Hint 1

What does `dis.get_instructions(f)` yield, and which attribute of each item is the name?
How do you turn "a stream of names" into "name -> how many" in one line?
For the recursive part: where does an inner function's code live, and how do you recognise a
code object among the constants (`isinstance(x, types.CodeType)`)? A nested code object can
contain more code objects: what kind of function handles "the same job, one level deeper"?

## Hint 2

```
opcode_histogram(obj, recursive):
    code = obj if it is a code object else obj.__code__
    hist = Counter(ins.opname for ins in dis.get_instructions(code))
    if recursive:
        for const in code.co_consts:
            if const is a code object:
                hist += opcode_histogram(const, recursive=True)
    return hist

by_prefix(hist):
    result = Counter()
    for name, count in hist.items():
        result[name.split("_", 1)[0]] += count
    return result
```
