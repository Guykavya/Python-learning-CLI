# Control total and bridge

Chapters 11.2 to 11.4. A report grid says 1,282,055.95 but the total of the order lines says 1,296,540.10. A good analyst does not stop at "the numbers do not match": she builds a **bridge** from the grid to the total, with each cause and its amount, until **nothing is left unexplained**.

The grid is made with `SUMIFS` on the region and (through a lookup) the product category. A line falls **out of the grid** when:

1. its **product code is not found** in the product table: Excel's lookup is case-insensitive but exact about spaces, so `p07` is found and `P07 ` (a trailing space) and `PO5` are not; a code is found when `str(code).upper()` is in `valid_codes` (a set of upper-case codes);
2. its **region is not matched**: SUMIFS ignores case but not spaces, so a region is matched when `str(region).lower()` is in the lower-case list of `regions` (`"North "` with a trailing space is not).

Write `bridge(df, regions, valid_codes)`. `df` has `region`, `units` (numbers, or numbers stored as **text**: Excel multiplies them as numbers, so convert with `float`), `unit_price`, `discount` and `product_code`. The revenue of a line is `units x unit_price x (1 - discount)`.

Return a dict:

| key | meaning |
|---|---|
| `control_total` | the revenue of **all** lines |
| `grid_total` | the revenue of the lines with a **found code and a matched region** |
| `gap` | `control_total - grid_total` |
| `causes` | `{"product code not found": amount, "region not matched": amount}`: the first cause takes every line whose code is not found; the second takes the **remaining** lines whose region is not matched |
| `unexplained` | `gap - sum of the causes` |

## Example

A line of revenue 100 with the code `P07 ` goes to `product code not found`; a line of revenue 50 with the region `North ` and a valid code goes to `region not matched`; a line with both faults is counted once, under the first cause.
