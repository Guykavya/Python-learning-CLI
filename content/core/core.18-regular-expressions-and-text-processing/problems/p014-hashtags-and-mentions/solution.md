## Approach

1. **Find**: `#(\w+)` finds `#` plus a name, and the group makes `findall` return only the name.
2. **Not glued to a word**: put `\B` in front. `\B` matches where `\b` does not, that is between
   two word characters or between two non-word characters. `#` and `@` are non-word characters,
   so `\B#` succeeds only if the character before `#` is also a non-word character, or if the
   `#` is at the start of the text. `a#b` and `kavya@example.com` fail; ` #b` and `(#b` pass.
3. **Clean up**: lower-case hashtags, then remove repeats while keeping first-seen order.

## Code

```python
import re

HASHTAG_RE = re.compile(r"\B#(\w+)")
MENTION_RE = re.compile(r"\B@(\w+)")


def _unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def tags(text: str) -> dict[str, list[str]]:
    hashtags = [h.lower() for h in HASHTAG_RE.findall(text)]
    mentions = MENTION_RE.findall(text)
    return {"hashtags": _unique(hashtags), "mentions": _unique(mentions)}
```

## Complexity

O(n) for a text of length n: two scans plus linear de-duplication with a set.

## Another way

- A **lookbehind** says the rule directly: `(?<!\w)#(\w+)` means "`#` not preceded by a word
  character". It is easier to read than `\B` once you know lookarounds.
- `list(dict.fromkeys(items))` removes repeats and keeps order in one line, because dict keys
  are unique and remember insertion order.
- One pattern for both: `\B([#@])(\w+)` with `findall` gives `(symbol, name)` tuples; then
  sort them into the two lists in a loop.
