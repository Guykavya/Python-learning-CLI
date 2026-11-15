## Hint 1

Ask three questions for each scenario. Is it about **one contiguous stretch** or **many queries**? Are the values all
**positive**, or can they be negative? Is the input **sorted**, or is the window size **fixed**?

## Hint 2

Map the answers:

```
many range-sum queries, no updates        -> prefix sums
many range updates, read once at the end  -> difference array
pair in a sorted array                    -> two pointers from both ends
best contiguous sum, negatives allowed    -> Kadane
shortest/longest stretch, all positive    -> variable sliding window
same, but negatives allowed               -> prefix sums + dictionary / monotonic deque
```

## Hint 3

For each trap, change one property: make the values negative, unsort the input, add updates between the queries, or
ask for "exactly" instead of "at least". Which tool then fails, and what replaces it?
