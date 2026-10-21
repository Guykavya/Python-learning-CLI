# Blank or shout

Read one line of text.

- If the line is **blank** (empty, or only spaces), print `(blank)`.
- Otherwise, remove spaces at both ends, change it to capital letters, and make sure it
  ends with exactly one `!`. If it already ends with `!`, do not add another.

Use `input()` without a prompt.

**Examples**

| Input | Output |
|---|---|
| `hello` | `HELLO!` |
| `   wow!  ` | `WOW!` |
| (only spaces) | `(blank)` |
| `0` | `0!` |

Use truthiness: test the string itself, not its length.
