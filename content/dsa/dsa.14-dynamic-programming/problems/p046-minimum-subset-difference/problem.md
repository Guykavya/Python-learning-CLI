# Minimum subset difference

Two friends split a pile of parcels with weights `nums`. Every parcel goes to exactly one friend. Make the two loads **as equal as possible**.

Write `split_evenly(nums)` that returns a pair `(difference, group)`:

- `difference` is the smallest possible `|load A - load B|`;
- `group` is a list of **indices** of the parcels that friend A carries (friend B carries the rest), and it must reach that smallest difference.

## Example

```python
>>> split_evenly([1, 6, 11, 5])
(1, [2])                        # A: 11, B: 1 + 6 + 5 = 12
>>> split_evenly([3, 1, 4, 2, 2])
(0, [0, 1, 3])                  # A: 3 + 1 + 2 = 6, B: 4 + 2 = 6
>>> split_evenly([10])
(10, [])                        # one friend gets nothing
```

Many groups can be optimal (`[0, 1, 3]` is also right for the first example: 12 against 11, still a difference of 1). The tests **check** your group instead of comparing it with one fixed list: the indices must be different, valid, and give the difference you returned, and that difference must be the smallest possible. The order of the indices does not matter.

## Constraints

- `1 <= len(nums) <= 100`, `1 <= nums[i] <= 100`.
- Time `O(n * total)`. Trying every split does not finish for 100 parcels.

## Think about

Which subset sums are reachable (chapter section 12)? Which one gives the smallest difference? Then: how do you find **which** parcels make that sum? Chapter section 9 ("re-derive the choice from the table") and section 10 ("Which items were taken?") walk back through a table. What table do you need to keep for that?
