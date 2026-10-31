## Approach

Compare the pattern with the rules piece by piece. There are five separate bugs:

| Piece | Bug | Symptom |
|---|---|---|
| `.+` after `@` | greedy and matches spaces | two addresses (and the text between) become one |
| `.` before the TLD | not escaped, matches any character | `admin@localhost` = `localhos` + `t` |
| `[a-z]+` | small letters only, length 1 allowed | capitals missed or cut, `x@y.z` accepted |
| `[\w.+-]` | `%` is missing | the match starts after the `%` |
| (end) | nothing stops the TLD running into more text | `bob@site.com2` gives `bob@site.co` |

Rebuild the domain from its definition instead of patching `.+`:

```
(?:[A-Za-z0-9-]+\.)+    one or more labels, each followed by a real dot
[A-Za-z]{2,}            the top-level part, 2+ letters, either case
\b                      and it must end there
```

Because labels cannot contain spaces, the match cannot run into the next address. The final
full stop of a sentence is not taken: after `com` the `\.` would need another label and a TLD.
`\b` makes `site.com2` fail; backtracking to `site.co` does not help, because `co` is followed
by `m`, a word character, so `\b` fails there too.

## Code

```python
import re

EMAIL_RE = re.compile(r"[\w.%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")


def extract_emails(text: str) -> list[str]:
    """Every email address in `text`, in order, spelled as written."""
    return EMAIL_RE.findall(text)
```

The group is non-capturing on purpose: with a capturing group, `findall` would return the
last label instead of the whole address.

## Complexity

O(n) in practice. The nested `(...+\.)+` can backtrack, but every label must end with a dot,
so the engine has only one way to split a domain into labels.

## Another way

Use `re.IGNORECASE` and write `[a-z0-9-]` and `[a-z]{2,}`. The result is the same.
For real validation of a single address, do not trust a regex alone: the full email grammar is
huge. The usual practice is a simple pattern like this one plus sending a confirmation mail.
