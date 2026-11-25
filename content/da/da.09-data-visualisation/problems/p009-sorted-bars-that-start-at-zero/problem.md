# Sorted bars that start at zero

Chapter section 4. To compare categories, use **horizontal bars, sorted, from a zero baseline**: long names fit, the eye ranks them at once, and
the bar length is honest.

Write `category_bars(df, cat, val)`. `df` has one or more rows per category; add up `val` for each `cat` and draw a horizontal bar chart:

- the **largest** category is the **top** bar, then descending down the page;
- the value axis (x) starts at 0;
- the x label is the name of `val`.

Return the Figure.

## Example

For `store = A, B, C` with totals `150, 400, 220`, the top bar is B, then C, then A.

Hint about `barh`: it draws the first bar at the **bottom**.
