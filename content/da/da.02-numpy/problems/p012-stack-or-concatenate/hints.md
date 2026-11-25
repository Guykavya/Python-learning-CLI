## Hint 1

For each call, decide first: does it **lengthen** an axis that exists (concatenate, vstack, hstack) or **add** a new axis of length 2 (stack)? If it adds one, at which position does the 2 go in the shape?

## Hint 2

```text
concatenate (axis 0): add the lengths on axis 0          (3,)+(3,) -> (6,)    (2,3)+(2,3) -> (4,3)
stack axis=a: insert a 2 at position a in the shape       (3,) -> (2,3) / (3,2);  (2,3) -> (2,2,3) / (2,2,3) / (2,3,2)
vstack: 1-D inputs become rows first                      -> (2,3);   2-D -> like concatenate axis 0
hstack: 1-D joins end to end                              -> (6,);    2-D -> axis 1
column_stack: 1-D inputs become columns                   -> (3,2);   2-D -> like hstack
```
