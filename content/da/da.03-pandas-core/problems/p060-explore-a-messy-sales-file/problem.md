# Explore a messy sales file

**The project of the chapter (section 19).** A small shop gives you its January to June 2025 sales export as a messy CSV
and asks six questions. Write `explore(path, out_dir)` that does the whole job and **returns the six answers**.
Everything you need is in your own `solution.py` (copy and adapt the helpers of chapter 18.2); nothing is imported from
a course module.

**Test data.** The test writes the chapter's file with `make_messy_sales(path)` of chapter 19.1 (defaults: 1,200 orders,
seed 11, which gives 1,235 rows: 30 exact duplicates and 5 clashing order ids). Copy that function from the chapter if
you want to experiment in `my-work/`.

## What `explore` does

1. **Load.** Read every column as text (`dtype="str"`). Drop rows that are **exact duplicates of an earlier row**
   (compare the raw text of all ten columns) and remember how many were dropped. Then convert:

   | column | conversion |
   |---|---|
   | `customer`, `city` | strip, collapse inner spaces, title case |
   | `product`, `category` | strip, collapse inner spaces, lower case |
   | `unit_price` | money (`₹`, `Rs.`, `INR`, commas), missing when it is not a number |
   | `discount` | `"5%"` gives `0.05`; a number above 1 is a percent (divide by 100); `"0.15"` stays `0.15` |
   | `order_date` | formats `%Y-%m-%d`, `%d/%m/%Y`, `%b %d, %Y` in this order; `NaT` when none fits (`31/02/2025`) |
   | `paid` | yes/y/true/1 are `True`, no/n/false/0 are `False`, anything else missing |
   | `qty` | whole numbers as `Int64`; anything else missing |
   | `order_id` | stays text |

2. **Flag, do not delete.** Add four boolean columns (`True` = problem, never missing): `flag_date` (missing, or outside
   2025-01-01 to 2025-06-30), `flag_qty` (missing, below 1 or above 50), `flag_price` (missing, below 10 or above 20,000),
   `flag_id` (the `order_id` appears more than once after the duplicates are gone: mark **all** its rows). Add
   `usable = not any flag`, and `revenue = qty * unit_price * (1 - discount)` with a missing discount counting as 0.

3. **Write** into `out_dir` (create it if it does not exist; running twice overwrites):
   - `clean.parquet`: all rows in file order, columns exactly
     `order_id, order_date, customer, city, product, category, qty, unit_price, discount, paid, flag_date, flag_qty,
     flag_price, flag_id, usable, revenue` (no index);
   - `problems.csv`: columns `problem,rows` with six lines in this order: `exact_duplicates_removed`, `flag_date`,
     `flag_qty`, `flag_price`, `flag_id`, `any_flag` (rows with at least one flag).

4. **Answer** on the **usable** rows only, and return a dict with exactly these keys:

   | key | value |
   |---|---|
   | `"revenue"` | total revenue (`float`) |
   | `"best_month"` | the month with the highest revenue as `"YYYY-MM"` (a tie: the earlier month) |
   | `"top5"` | the `order_id`s (text) of the five biggest orders by revenue, biggest first (a tie: smaller id first) |
   | `"busiest_weekday"` | the English weekday name with the most orders (a tie: alphabetical) |
   | `"unpaid_share"` | the share of revenue whose `paid` is **not** `True` (unpaid or unknown) |
   | `"discount_cost_share"` | `(gross - revenue) / gross` where `gross = qty * unit_price` (the share given away in discounts) |

The test checks every file and every answer against its own plain-Python computation from the raw CSV.

## Example

On the chapter's file (`make_messy_sales(path)` with the defaults), a correct solution gives these answers
(the same numbers as chapter 19, pandas 3.1.1):

```text
usable orders 1142, revenue 4,194,964.35, best month 2025-03
```

`problems.csv` starts like this (the first line is the header):

```text
problem,rows
exact_duplicates_removed,30
flag_date,13
```

## After you finish

- Which of the six answers would change if you dropped the five clashing order ids *and* kept one of each pair instead of flagging both rows?
- The two prices that are 100 times too large are flagged, not corrected. Why is that the honest choice?
