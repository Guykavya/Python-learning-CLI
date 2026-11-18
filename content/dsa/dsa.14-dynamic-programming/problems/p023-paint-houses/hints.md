## Hint 1

"The cheapest way to paint the first `i` houses" is not enough: to choose a colour for house `i` you must know the colour of house `i - 1`. Put it in the state. `f[i][c]` = the cheapest way to paint houses `0..i` with house `i` painted colour `c`. Base: `f[0][c] = costs[0][c]`.

## Hint 2

If house `i` has colour 0, house `i - 1` had colour 1 or 2: `f[i][0] = costs[i][0] + min(f[i-1][1], f[i-1][2])`. Write the other two lines. Row `i` reads only row `i - 1`: how many numbers do you need to keep?

## Hint 3

```
if no houses: return 0
red, green, blue = costs[0]
for each later row (c0, c1, c2):
    red, green, blue = c0 + min(green, blue), c1 + min(red, blue), c2 + min(red, green)
return min(red, green, blue)
```

The tuple assignment uses the **old** three values on the right side (section 6).
