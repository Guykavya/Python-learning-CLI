## Hint 1

`iter(f, sentinel)` calls `f()` again and again and stops when the result equals `sentinel`. So you
need a function with **no arguments** that returns "the next page". How can a function with no
arguments know which page is next? Think of a closure from the Functions module.

## Hint 2

Inside `pages`, keep `page_number = 0`. The inner function uses `nonlocal page_number`. Only add 1
after a **successful** fetch, so a retry asks for the same page. For the retries, a `while True`
loop with `try / except ConnectionError / else` works well; a bare `raise` re-raises the current error.

## Hint 3

```
pages(fetch_page, retries):
    page_number = 0
    def next_page():
        nonlocal page_number
        attempts_left = retries
        loop:
            try: page = fetch_page(page_number)
            except ConnectionError:
                if attempts_left == 0: raise
                attempts_left -= 1
            else:
                page_number += 1
                return page
    return iter(next_page, [])

items(...):
    for page in pages(...): yield from page
```
