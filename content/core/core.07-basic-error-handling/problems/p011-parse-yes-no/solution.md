## Approach

Validate the type, normalise the text, then look it up in two small tuples. If neither matches,
the final line raises. The message uses the **original** text with `!r`, so the user sees exactly
what they typed, including spaces and empty answers.

## Code

```python
YES = ("yes", "y", "true", "1")
NO = ("no", "n", "false", "0")


def parse_yes_no(text):
    """Return True or False for a yes/no answer; raise ValueError if it is neither."""
    if not isinstance(text, str):
        raise TypeError(f"answer must be text (str), got {type(text).__name__}")
    word = text.strip().lower()
    if word in YES:
        return True
    if word in NO:
        return False
    raise ValueError(f"answer must be yes or no (also y/n, true/false, 1/0), got {text!r}")
```

## Complexity

O(n) in the length of the text; the tuple lookups are constant size.

## Another way

A dict `{"yes": True, "y": True, ..., "no": False}` and an EAFP lookup `ANSWERS[word]` with
`except KeyError: raise ValueError(...) from None`. That is neat, and shows translating one
exception into a clearer one (section 11).
