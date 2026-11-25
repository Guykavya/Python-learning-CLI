# A lookup is a left join

Chapter section 7.5. A product code appears **twice** in the price table: `P05` with unit cost 24.00 and again with 29.00 (a price change was added at the bottom). The orders table has 120 lines for `P05`.

In `answer.md`, in about 200 to 300 words:

1. what `XLOOKUP` / `VLOOKUP` returns for the 120 lines of `P05`, and what happens to the other duplicate;
2. what `orders.merge(products, on="code", how="left")` returns, and what `validate="m:1"` would do;
3. why the **total cost** differs between the Excel report and the pandas result, and which of the two is "right";
4. what you would do before writing the lookup.

## Example

A start: "A lookup is a left join that takes only the **first** match: all 120 lines get the cost 24.00, and the 29.00 row is never used. A pandas merge keeps **both** matches, so each of the 120 lines appears twice (a row **fan-out**) ..."
