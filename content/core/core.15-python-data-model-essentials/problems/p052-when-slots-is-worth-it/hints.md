## Hint 1

Where does `a.x` come from for a normal object? Look at the second printed line: how many bytes does the dictionary add per object? Multiply that by the number of objects you create in a big program.

## Hint 2

Think of the cost and the rule you pay: no new attributes at run time, no `vars(obj)`. Which programs create hundreds of thousands of tiny objects, and which create ten? `tracemalloc` (from the standard library) reports memory used by Python objects.
