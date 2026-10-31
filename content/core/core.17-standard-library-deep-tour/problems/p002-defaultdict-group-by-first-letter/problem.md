# defaultdict: group words by first letter

"Group these things by some key" is a pattern you will write hundreds of times. With a plain
dict you must check `if key not in groups: groups[key] = []` every time. A
`collections.defaultdict(list)` creates the empty list for you the first time a key is used.

Write two functions in `solution.py`. Use a `defaultdict` inside each one.

1. `group_by_first_letter(words: list[str]) -> dict[str, list[str]]`
   - The key is the **lower-case** first letter of the word; the list keeps the words (as given,
     not lower-cased) in **input order**.
   - Skip empty strings.
2. `count_by_length(words: list[str]) -> dict[int, int]`
   - How many words have each length (empty strings count too, with length `0`).

Both functions must return a **plain `dict`**, not the `defaultdict`. A caller who reads a
missing key by mistake should get a `KeyError`, not a silently created empty entry.

**Example**

```python
group_by_first_letter(["apple", "Bob", "avocado", "", "banana"])
# {'a': ['apple', 'avocado'], 'b': ['Bob', 'banana']}

count_by_length(["hi", "yo", "hey"])
# {2: 2, 3: 1}
```
