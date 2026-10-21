# Choose from a menu, by number or name

Write `choose(options, ask=input, tell=print)` that lets a user pick one item from the list
`options` and returns that item.

- If `options` is empty, raise `ValueError("options must not be empty")` without asking.
- Ask with the prompt `f"Choose 1-{len(options)} or a name: "`, using `ask(prompt)`.
- The answer (after `strip()`) may be:
  - a number from 1 to `len(options)`: return `options[number - 1]`;
  - an option's name, ignoring case: return the option as it appears in `options`.
- Anything else: `tell(f"{text!r} is not an option. Type a number from 1 to {len(options)} or a name.")`
  where `text` is the original answer, then ask again. Keep asking until the answer is valid.
- `0` and negative numbers are **not** valid choices (do not let Python's negative indexes sneak
  in).
- If `ask` raises `EOFError`, let it propagate.

Use `try`/`except ValueError` around `int()` to decide whether the answer is a number.

**Example**

```python
answers = iter(["seven", "0", "Coffee"])
messages = []
choose(["tea", "coffee", "juice"], ask=lambda p: next(answers), tell=messages.append)
# 'coffee'
messages
# ["'seven' is not an option. Type a number from 1 to 3 or a name.",
#  "'0' is not an option. Type a number from 1 to 3 or a name."]
```
