# When is a stored total worth it?

The orders page lists 50 orders with their **total** each. In the normalised schema an order has no total column: the page computes it with `SUM(qty * price_paise)` over the order's lines. The page has become slow for customers with thousands of orders, and a colleague suggests adding a column `orders.total_paise` that stores the total.

In `answer.md` (10 to 14 sentences), discuss chapter sections 3.6 and 3.7:

1. What does the stored total gain, and what does it cost? (Think of reads and writes.)
2. Which new kind of bug becomes possible? Give an example.
3. How do you keep the stored value correct? Name **two** measures.
4. Write (in words or SQL) a **reconciliation query** that finds orders whose stored total is wrong.
5. When would you **not** store it?
