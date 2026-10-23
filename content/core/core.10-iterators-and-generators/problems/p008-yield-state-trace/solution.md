## Approach

Creating the generator prints nothing (`created` comes first, before `start`). `next(g)` runs the body up to the first `yield`: it prints `start` and gives 1, which the outer `print` prints. The generator is frozen at that `yield`. The second `next` resumes after the first `yield`, prints `middle`, and gives 2. The third `next` resumes, prints `end`, and the body ends, which raises `StopIteration`. After that `list(g)` is empty.

## Output

```text
created
start
1
between
middle
2
end
stop
[]
```

## Complexity

O(1).

## Another way

Add `print('got', next(g))` for each call and see how the text of the generator and the main code alternate.
