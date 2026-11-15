# Largest rectangle in a histogram

A histogram has bars of width 1 standing side by side; `heights[i]` is the height of bar `i`. Write `largest_rectangle(heights)` that returns the area of the largest rectangle that fits entirely inside the bars.

The best rectangle's height is the height of its **shortest** bar. So for every bar, ask how far a rectangle of exactly its height can stretch: to the left until the previous **smaller** bar, to the right until the next **smaller** bar. An **increasing** stack of indices finds both in one pass (chapter section 10). A sentinel bar of height 0 at the end forces everything to be popped.

## Example

```python
>>> largest_rectangle([2, 1, 5, 6, 2, 3])
10
>>> largest_rectangle([2, 4])
4
>>> largest_rectangle([6, 2, 5, 4, 5, 1, 6])
12
>>> largest_rectangle([])
0
```

In the first example the bars 5 and 6 form a rectangle of height 5 and width 2.

## How it is tested

Fixed cases, 1,000 random small histograms compared with a brute force, and 100,000 bars with a time limit (the brute force needs billions of steps there).

## Constraints

- `0 <= len(heights) <= 10**5`, `0 <= heights[i] <= 10**4`. Do not change `heights`.

## Think about

When bar `j` is popped because a lower bar `i` arrives, which bar is its left boundary? Why is that bar sitting right below it in the stack?
