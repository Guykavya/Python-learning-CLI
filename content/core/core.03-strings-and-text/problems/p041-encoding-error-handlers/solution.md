## Code

```python
text = input()
kept = text.encode("ascii", errors="ignore").decode("ascii")
print(f"ignore: {kept}")
print(f"replace: {text.encode('ascii', errors='replace').decode('ascii')}")
print(f"xml: {text.encode('ascii', errors='xmlcharrefreplace').decode('ascii')}")
print(f"backslash: {text.encode('ascii', errors='backslashreplace').decode('ascii')}")
print(f"Lost: {len(text) - len(kept)}")
```

## What each handler means

| Handler | Information kept? | Typical use |
|---|---|---|
| `ignore` | no, characters vanish | almost never |
| `replace` | no, but you see that something was there | showing messy text to a person |
| `xmlcharrefreplace` | yes, as HTML entities | writing HTML or XML in ASCII |
| `backslashreplace` | yes, as Python escapes | logs and debugging |

## Why decode with ASCII is safe here

After any of these handlers, the bytes contain only ASCII, so decoding with `"ascii"` cannot fail.
