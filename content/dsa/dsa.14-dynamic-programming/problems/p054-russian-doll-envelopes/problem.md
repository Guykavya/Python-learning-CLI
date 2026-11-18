# Russian doll envelopes

Each envelope is a pair `(width, height)`. One envelope fits inside another only if it is **strictly smaller in both** width and height. You cannot rotate envelopes. Write `max_envelopes(envelopes)` that returns the largest number of envelopes you can nest one inside the other, like Russian dolls.

## Example

```python
>>> max_envelopes([(5, 4), (6, 4), (6, 7), (2, 3)])    # (2,3) -> (5,4) -> (6,7)
3
>>> max_envelopes([(1, 1), (1, 1), (1, 1)])            # equal envelopes do not nest
1
>>> max_envelopes([(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)])
4
>>> max_envelopes([])
0
```

In the third example `(1,1) -> (2,3) -> (4,5) -> (6,7)` has 4 envelopes. `(4, 5)` and `(4, 6)` have the same width, so they can never both be in the chain.

## Constraints

- `0 <= len(envelopes) <= 10**5`, `1 <= width, height <= 10**5`. Envelopes may be given as tuples or lists.
- Time `O(n log n)`. The test has 100,000 envelopes with a time limit.

## Think about

If the envelopes were sorted by width, and all widths were different, the answer would be the LIS of the heights (chapter section 13, "Variations that reuse LIS"). Equal widths break that. With envelopes `(3, 3)` and `(3, 4)`, sorted by width and then height, the heights `3, 4` look increasing, but the envelopes do not nest. How should envelopes with the **same width** be ordered so that the LIS can never pick two of them?
