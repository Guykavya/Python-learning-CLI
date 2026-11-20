# Huffman code lengths

`freq` is a dictionary `letter -> count` (every count at least 1). Using Huffman's algorithm from chapter section 13, write:

1. `code_lengths(freq)`: a dictionary `letter -> number of bits` in that letter's Huffman code (its depth in the Huffman tree).
2. `total_bits(freq)`: the number of bits needed to encode the whole text, `sum(freq[x] * length[x])`.

A text with **one** distinct letter still needs 1 bit per letter (the chapter's convention: the lone letter gets the code `"0"`).

## Example

```python
>>> freq = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
>>> code_lengths(freq) == {"a": 1, "b": 3, "c": 3, "d": 3, "e": 4, "f": 4}
True
>>> total_bits(freq)
224
>>> code_lengths({"z": 7}), total_bits({"z": 7})
({'z': 1}, 7)
```

## Ties

When counts are equal, Huffman can build different trees with **different** code lengths but the **same** total. For `{"a": 1, "b": 1, "c": 2, "d": 2}` both `2, 2, 2, 2` and `3, 3, 2, 1` cost 12 bits. So the tests do **not** check your exact lengths. They check that:

- the lengths could belong to a prefix-free code (they fit in a binary tree: `sum(2 ** -length) <= 1`, the Kraft inequality);
- the total is the smallest possible (compared with a brute force that tries every order of joins, for up to 6 letters, and with the chapter's implementation).

## Constraints

- `1 <= len(freq) <= 10**4`, counts up to `10**6`. Use a heap: re-sorting a list after every join is too slow for 10,000 letters.
- Equal counts are common in the tests. Remember the chapter's **tie-breaker trap**.

## Think about

Do you need to build the tree at all to know the depths? What happens to the depth of every letter inside two trees when those trees are joined?
