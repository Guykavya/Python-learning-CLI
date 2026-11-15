# Add two numbers stored as lists

A non-negative integer is stored as a linked list of its digits **in reverse order**: the head is the ones digit. So `342` is `2 -> 4 -> 3`.

Write `add_two_numbers(a, b)` that returns the sum as a **new** list in the same format. Do not change the input lists. Do not convert the lists to Python integers: add digit by digit with a carry, as on paper.

## Example

```text
  2 -> 4 -> 3        (342)
+ 5 -> 6 -> 4        (465)
= 7 -> 0 -> 8        (807)
```

```python
>>> to_list(add_two_numbers(from_list([2, 4, 3]), from_list([5, 6, 4])))
[7, 0, 8]
>>> to_list(add_two_numbers(from_list([9, 9]), from_list([1])))      # 99 + 1 = 100
[0, 0, 1]
>>> to_list(add_two_numbers(from_list([0]), from_list([0])))
[0]
```

## Constraints

- Each list has `1` to `10**4` nodes, each digit is `0..9`, and there are no leading zeros except the number `0` itself (`[0]`).

## Think about

Why does the reversed order make addition easy (where does paper addition start)? What must happen when both lists are used up but the carry is still `1`?
