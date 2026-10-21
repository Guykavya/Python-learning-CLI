# An inventory command processor

A shop assistant types commands to manage stock. Write `process(commands, stock)` where
`commands` is a list of command strings and `stock` is a dict from item name to quantity, which
the commands change in place. Return a list with **one reply per command**.

| Command | Effect | Reply |
|---|---|---|
| `add <item> <qty>` | add `qty` to the item (a new item starts at 0) | `<item>: <new qty>` |
| `remove <item> <qty>` | subtract `qty` | `<item>: <new qty>` |
| `show <item>` | nothing | `<item>: <qty>` |
| `list` | nothing | `<item>: <qty>` for every item, sorted by name, joined with `", "`; or `empty` |

Item names are case-insensitive: store and show them lower-case. Words are separated by
whitespace.

**Errors.** A bad command never stops the processing of later commands; its reply starts with
`"error: "`:

- empty command: `error: empty command`
- unknown verb: `error: unknown command <verb!r>; use add, remove, show or list`
- wrong number of words: `error: usage: add <item> <qty>` (or `remove <item> <qty>`,
  `show <item>`, `list`)
- quantity not a positive whole number: `error: quantity must be a positive whole number, got <qty!r>`
- `remove` or `show` of an item not in stock: `error: no item <item!r> in stock`
- `remove` more than there is: `error: only <have> <item> in stock, cannot remove <qty>`
  (and the stock does not change)

**Design.** Write one handler function per verb, `handler(stock, words)` where `words` are the
words after the verb, and keep them in a dict (a dispatch table, chapter 6). Handlers do the work
and **raise** `ValueError` (with the message after `error: `) or let a `KeyError` from a missing
item escape. `process` is the **boundary**: it looks up the handler, calls it, and translates
exactly those two exception types into `error:` replies. Any other exception is a bug and must
propagate.

**Example**

```python
stock = {"apple": 5}
process(["add Banana 12", "remove apple 2", "remove apple 9", "show kiwi",
         "add pear lots", "sell apple 1", "list"], stock)
# ['banana: 12',
#  'apple: 3',
#  'error: only 3 apple in stock, cannot remove 9',
#  "error: no item 'kiwi' in stock",
#  "error: quantity must be a positive whole number, got 'lots'",
#  "error: unknown command 'sell'; use add, remove, show or list",
#  'apple: 3, banana: 12']
```
