# Friendly menu prices

A café keeps its menu as a dict from item name to price in rupees. Write
`price_message(menu, item)` that returns a sentence for the customer.

- If `item` is on the menu: `"<item> costs Rs <price>"`.
- If it is not: `"Sorry, <item!r> is not on the menu. Choose one of: <items>."` where `<items>` are
  the menu's items **sorted** alphabetically and joined with `", "`.
- If the menu is empty: `"Sorry, <item!r> is not on the menu. The menu is empty today."`

Use `try`/`except KeyError` for the lookup (EAFP). Put the success sentence in an `else` block or
after the `try` statement, so the `try` block contains only the lookup. If `item` cannot be a dict
key at all (for example a list), the lookup raises `TypeError`: that is a bug in the caller, so do
not catch it.

**Examples**

```python
menu = {"tea": 15, "coffee": 25, "samosa": 20}
price_message(menu, "tea")      # 'tea costs Rs 15'
price_message(menu, "cake")     # "Sorry, 'cake' is not on the menu. Choose one of: coffee, samosa, tea."
price_message({}, "tea")        # "Sorry, 'tea' is not on the menu. The menu is empty today."
```
