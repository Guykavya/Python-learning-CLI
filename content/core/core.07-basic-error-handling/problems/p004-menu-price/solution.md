## Approach

Only `menu[item]` can fail in the expected way, so it is the whole `try` block. The handler builds
the apology, choosing between two sentences with a truthiness test on the menu. The success
sentence goes in `else`, so a mistake in building it could never be mistaken for a missing item.
`sorted(menu)` sorts the keys; `", ".join` glues them together.

## Code

```python
def price_message(menu, item):
    """Return a customer-friendly sentence about the price of item."""
    try:
        price = menu[item]
    except KeyError:
        if not menu:
            return f"Sorry, {item!r} is not on the menu. The menu is empty today."
        return f"Sorry, {item!r} is not on the menu. Choose one of: {', '.join(sorted(menu))}."
    else:
        return f"{item} costs Rs {price}"
```

## Complexity

O(1) for a found item; O(m log m) to sort the m menu items for a missing one.

## Another way

`price = menu.get(item)` followed by `if price is None:` is the LBYL-flavoured alternative and is
perfectly good Python. It needs care if `None` could ever be a real price. The problem asks for
the `try` version to practise `else`.
