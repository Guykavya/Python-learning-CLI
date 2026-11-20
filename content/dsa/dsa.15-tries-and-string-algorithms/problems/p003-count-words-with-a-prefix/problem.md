# Count words with a prefix

A shop logs every product name a customer searches for, duplicates included. Write a class `CountTrie` (chapter section 5, "Counts on the nodes") with:

- `insert(word)`: log one more search for `word`;
- `count_equal(word)`: how many logged words are exactly `word`;
- `count_prefix(prefix)`: how many logged words start with `prefix` (every copy counts).

Both counts must cost `O(len(text))`, whatever the number of logged words: store two numbers on every node.

## Example

```python
>>> ct = CountTrie()
>>> for w in ["car", "car", "card", "care", "cat", "dog"]:
...     ct.insert(w)
>>> ct.count_equal("car"), ct.count_equal("ca")
(2, 0)
>>> ct.count_prefix("car"), ct.count_prefix("ca"), ct.count_prefix("z")
(4, 5, 0)
>>> ct.count_prefix("")      # every logged word starts with ""
6
```

## Constraints

- Words may contain any characters, and may be empty.
- Up to 10**5 inserts and 10**5 queries in the tests.

## Think about

1. Which number does a node need for `count_prefix`, and which for `count_equal`?
2. Which node's count answers `count_prefix("")`? Is the root's number updated by your `insert`?
3. Where in `insert` do the two numbers change?
