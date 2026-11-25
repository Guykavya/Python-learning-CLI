# Stacked bars of shares

Chapter section 4.5. To show **what share** each part has of a whole, in several groups, use a **100% stacked bar**: every bar has the same
total height (100), so only the shares differ.

Write `share_bars(df, group, part, value)`. `df` has one row per (`group`, `part`) with the number `value` (some pairs may repeat: add them).

- one bar per group, in the order the groups **first appear** in `df`;
- the parts are stacked **bottom to top** in the order they first appear in `df`;
- each bar's segments are percentages of that group's total, so the segments of one bar add up to **100**;
- a part missing in a group has a segment of height 0;
- draw each part with `ax.bar(..., bottom=...)` and `label=<part>`, and add a legend: its entries are in the **same order** as the stack, bottom to top.

Return the Figure.

## Example

Group `A` with parts `x = 30` and `y = 70` draws two segments, heights 30 and 70, stacked; group `B` with `x = 50, y = 50` draws 50 and 50.
