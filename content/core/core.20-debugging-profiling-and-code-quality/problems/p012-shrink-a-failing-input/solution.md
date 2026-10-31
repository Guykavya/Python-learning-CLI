## Approach

The rules say exactly when to stop: when no single element can be removed. So the core loop
is "try to remove something; if it still fails, keep the smaller list; stop after a full pass
with no success".

Two details make it correct:

- After a successful removal at position `i`, **stay at `i`**: a new element has moved into
  that position and has not been tried yet.
- Only stop after a pass with chunk size 1 that removed **nothing**. A pass that removed
  something may have changed what else can go (the failure is not always monotone), so run
  another pass.

To save calls, start with big chunks (half the list). Large irrelevant parts disappear in a few
calls; then halve the chunk size whenever a pass removes nothing, down to 1.

## Code

```python
def shrink(items: list, fails) -> list:
    current = list(items)
    if not fails(list(current)):
        raise ValueError("the input does not fail, nothing to shrink")
    chunk = max(len(current) // 2, 1)
    while current:
        removed = False
        i = 0
        while i < len(current):
            candidate = current[:i] + current[i + chunk:]
            if fails(list(candidate)):
                current = candidate
                removed = True
            else:
                i += chunk
        if not removed:
            if chunk == 1:
                break
            chunk = max(chunk // 2, 1)
    return current
```

`fails(list(candidate))` passes a fresh copy, so a `fails` that changes its argument cannot
damage our `current`.

## Complexity

Each successful call makes the list shorter, so there are at most n successful calls. Each pass
costs at most about n / chunk calls. For a few needed elements among n this is O(n) calls in
practice; the worst case (every element needed at the end, many passes) is O(n^2). Each call
also copies a list, O(n). Compare that with 2^n subsets.

## Another way

The plain version without chunks is shorter and also correct:

```python
def shrink(items, fails):
    current = list(items)
    if not fails(list(current)):
        raise ValueError
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(current):
            candidate = current[:i] + current[i + 1:]
            if fails(candidate):
                current, changed = candidate, True
            else:
                i += 1
    return current
```

Zeller's full **ddmin** algorithm also tries keeping just one chunk (not only removing one),
which shrinks some inputs faster. For real projects, property-based testing with Hypothesis
shrinks failing examples for you.
