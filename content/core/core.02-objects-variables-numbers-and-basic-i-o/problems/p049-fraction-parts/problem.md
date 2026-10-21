# Whole part and remainder of a fraction

Read a fraction like `22/7` or `-22/7`. Print five lines about it, using the `fractions` module:

```
floor: <f // 1>
remainder: <f % 1>
truncated: <int(f)>
rounded: <round(f)>
check: <True if floor + remainder equals f>
```

**Example**

Input:
```
-22/7
```
Output:
```
floor: -4
remainder: 6/7
truncated: -3
rounded: -3
check: True
```

Before coding, predict the output for `-22/7` yourself and compare. Then think about why
`floor` and `truncated` differ for negatives, and what `round` does with `5/2`.
