# Run-length encoding

Run-length encoding shortens text with repeated characters by writing each **run** (a group
of the same character in a row) as the character followed by the length of the run.

Read one line and print its encoding. Spaces count as characters. If the line is empty,
print `(empty)`.

**Examples**

| Input | Output |
|---|---|
| `aaabccdddd` | `a3b1c2d4` |
| `abc` | `a1b1c1` |
| `zzzzzzzzzzzz` | `z12` |
| `aabaa` | `a2b1a2` |

Note that the same character can start a new run later (`aabaa`).
