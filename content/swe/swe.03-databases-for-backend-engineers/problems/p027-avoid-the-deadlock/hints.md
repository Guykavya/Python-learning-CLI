## Hint 1

A deadlock needs a cycle: A waits for B and B waits for A. If every thread asks for the locks in the **same order**, can a cycle form?

## Hint 2

You do not know which account is "first": the transfer 1 -> 2 and the transfer 2 -> 1 involve the same two accounts but opposite roles. How can both calls agree on an order? (Sort the ids.)

## Hint 3

```text
first, second = sorted((src, dst))
with self.locks[first]:
    with self.locks[second]:
        check the balance of src; move the money
```
