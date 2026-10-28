# Lazy pagination with retries

Many web services give results in **pages**: you ask for page 0, page 1, page 2, ... and an empty
page means "no more data". Each request is slow, so a program should only fetch a page when it
really needs its items.

You get a function `fetch_page(n)` that returns a list with the items of page `n` (counting from 0).
An empty list means the end. Sometimes the network fails and `fetch_page` raises `ConnectionError`.

Write two functions in `solution.py`.

## 1. `pages(fetch_page, retries=2)`

Return an iterator over the **non-empty** pages: page 0, page 1, ..., stopping at the first empty page.

- Build it with **`iter(callable, sentinel)`**: write an inner function with no arguments that
  fetches the next page each time it is called (it remembers the page number with `nonlocal`),
  and use `[]` as the sentinel.
- If a fetch raises `ConnectionError`, try the **same page** again, up to `retries` extra times.
  If it still fails, let the `ConnectionError` reach the caller.
- Any other exception is **not** retried: it reaches the caller at once.

## 2. `items(fetch_page, retries=2)`

A generator over all items of all pages, in order, built on `pages()`. It must be lazy: if the
caller takes only 3 items and page 0 has 5 items, only page 0 is fetched.

**Example**

```python
data = [["a", "b", "c"], ["d", "e"], ["f"]]
calls = []

def fetch_page(n):
    calls.append(n)
    return data[n] if n < len(data) else []

it = items(fetch_page)
next(it), next(it)      # ("a", "b")
calls                   # [0]          only page 0 so far
list(it)                # ["c", "d", "e", "f"]
calls                   # [0, 1, 2, 3] page 3 was empty, so it stopped
```
