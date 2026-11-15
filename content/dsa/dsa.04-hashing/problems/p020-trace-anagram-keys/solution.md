## Walkthrough

| word | key | length of its group after append |
|---|---|---|
| listen | eilnst | 1 |
| silent | eilnst | 2 |
| enlist | eilnst | 3 |
| google | eggloo | 1 |
| gogole | eggloo | 2 |
| cat | act | 1 |
| act | act | 2 |

## Output

```
listen eilnst 1
silent eilnst 2
enlist eilnst 3
google eggloo 1
gogole eggloo 2
cat act 1
act act 2
eilnst ['listen', 'silent', 'enlist']
eggloo ['google', 'gogole']
act ['cat', 'act']
[2, 2, 3]
{6: 5, 3: 2}
```

## Key ideas

- All anagrams share one key; the key is built by sorting the letters and joining them to a string.
- `sorted(w)` returns a **list**, which is unhashable. `"".join(sorted(w))` makes a string, which is a valid key.
- Group sizes tell you how many words share a key; the dictionary order is the order of first appearance.
