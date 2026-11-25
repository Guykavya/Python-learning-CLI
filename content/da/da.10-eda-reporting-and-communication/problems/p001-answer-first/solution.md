## Approach

The numbers decide the verb, so the sentence cannot claim a rise that the data do not show. Comparing the **rounded** values keeps the words consistent with the digits the reader sees.

## Code

```python
def headline(metric, before, after, period, cause="", unit="%"):
    b, a = round(before, 1), round(after, 1)
    if a == b:
        text = f"{metric} stayed at {b:.1f}{unit} in {period}"
    else:
        verb = "rose" if a > b else "fell"
        text = f"{metric} {verb} from {b:.1f}{unit} to {a:.1f}{unit} in {period}"
    if cause:
        text += f", mainly because {cause}"
    words = len(text.split())
    if words > 40:
        raise ValueError(f"headline is {words} words (more than 40)")
    return text
```

## Complexity

O(length of the text).

## Another way

Return the parts (verb, numbers, cause) as a dict and let a template render them; the same rule (numbers decide the words) applies.
