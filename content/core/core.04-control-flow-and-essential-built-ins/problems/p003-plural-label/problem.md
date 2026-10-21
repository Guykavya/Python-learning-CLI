# Plural label

Read a whole number `n` (0 or more) on the first line and a singular noun on the second
line. Print a label:

- `n` is 0: `no <noun>s`
- `n` is 1: `1 <noun>`
- otherwise: `<n> <noun>s`

**Examples**

| Input | Output |
|---|---|
| `1` then `apple` | `1 apple` |
| `4` then `apple` | `4 apples` |
| `0` then `book` | `no books` |

**Rule for this problem:** do not use an `if` statement. Use **conditional expressions**
(`a if condition else b`). The tests check this.
