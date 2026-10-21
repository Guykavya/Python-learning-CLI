## Hint 1

Which expression can fail when the item is missing, and what does it raise? Only that
expression belongs in the `try` block.

## Hint 2

Inside the handler you need two different sentences. How do you test whether a dict is empty
(chapter 4, truthiness)?

## Hint 3

```
try:
    price = menu[item]
except KeyError:
    if menu is empty: return the 'empty today' sentence
    return the 'Choose one of' sentence with ", ".join(sorted(menu))
else:
    return f"{item} costs Rs {price}"
```
