## Code

```python
sentence = input()
old = input()
new = input()
print(sentence.replace(old, new))
print(f"Replacements: {sentence.count(old)}")
```

## Why count the original sentence

After replacing, the old word is gone, so counting in the new sentence gives 0 (or something wrong if the new word contains the old one). Count in the original.

## A detail

Both `replace` and `count` skip overlapping matches the same way. In `"aaaa"`, the text `"aa"` is found twice (at 0 and 2), and `replace` also makes two replacements. So the two always agree.
