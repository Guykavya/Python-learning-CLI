# Build a generic backtracking engine

Every backtracking problem in this module is the same template with three questions answered (chapter section 5): *what is a complete answer?*, *what are the options here?*, *what is not allowed?* Write the template **once**, as a function that takes those three answers as functions.

## Part 1: the engine

```python
def backtrack(choices, is_valid, is_done):
```

- `choices(path)` returns the options that may be appended to `path` next (any iterable; empty when the path cannot grow).
- `is_valid(path, option)` returns `True` if `option` may be appended to `path`.
- `is_done(path)` returns `True` if `path` is a complete answer.

Starting from the empty path, `backtrack` searches depth first: at each path it first checks `is_done(path)` and, if true, **records a copy** of the path; then (whether done or not) it tries every option from `choices(path)` **in the order given**, skipping options that are not valid, and for each valid one appends it, explores, and removes it again. It returns the list of recorded copies in the order they were found.

Your engine must pass the same list object `path` to the three functions; it must never let them see a path that contains an invalid option.

## Part 2: two users of the engine

Using `backtrack` (not your own loops or recursion), write:

- `subsets(nums)`: all subsets of the list `nums` (distinct items), each as a list with the items in their original order;
- `permutations(nums)`: all orderings of the list `nums` (distinct items).

The order of the subsets/permutations does not matter (the tests sort).

## Example

```python
>>> backtrack(lambda p: "ab" if len(p) < 2 else "",
...           lambda p, o: True,
...           lambda p: len(p) == 2)
[['a', 'a'], ['a', 'b'], ['b', 'a'], ['b', 'b']]
>>> sorted(subsets([1, 2]))
[[], [1], [1, 2], [2]]
>>> sorted(permutations([1, 2, 3]))[:2]
[[1, 2, 3], [1, 3, 2]]
```

## Think about

Because the engine records and then **keeps going**, `subsets` can use `is_done = lambda p: True` (every node is an answer). How can `choices` make sure that each subset is built only once? (Hint: what if each option must be bigger, by position, than the last one?)
