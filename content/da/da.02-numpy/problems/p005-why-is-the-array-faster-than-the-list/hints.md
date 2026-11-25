## Hint 1

Draw the list `[10, 20, 30]` as boxes: what is actually stored in the list's own memory, and where are the numbers? Now draw `np.array([10, 20, 30])`.

## Hint 2

```text
list loop, per element:  follow pointer -> check type -> find __mul__ -> new int object -> check type -> find __add__ -> new int object
numpy, once:             check dtype -> call C loop
numpy, per element:      load 8 bytes -> multiply -> add
```
Then add one sentence on tiny arrays.
