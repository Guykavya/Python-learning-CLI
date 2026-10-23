# Functions that return None: what prints?

Predict **exactly** what this program prints when you run it with `python`.

```python
def add_item(items: list[str], item: str) -> None:
    items.append(item)


def show(items: list[str]) -> None:
    print(len(items), "items")


cart: list[str] = []
r1 = add_item(cart, "tea")
r2 = show(cart)
print(r1, r2)
print(cart)
nums = [3, 1, 2]
print(nums.sort())
print(nums)
print(sorted([3, 1, 2]))
```

Write the printed lines, one per line, in order. (mypy flags the lines `r1 = ...` and `r2 = ...`
with `"add_item" does not return a value`, but the program still runs.)

Write your answer in `answer.txt`.
