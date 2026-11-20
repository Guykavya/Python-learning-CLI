# Is this migration safe?

Chapter section 13.8. A web application with several servers is **running while you deploy**: old code and new code are both alive for a few minutes, and the `orders` table has 50 million rows. For each of the six migrations below write **safe** or **unsafe**, say **why** in one or two sentences, and, if it is unsafe, the **safe sequence** of steps.

1. Rename the column `orders.total` to `orders.total_paise` in one step.
2. `ALTER TABLE orders ADD COLUMN note TEXT` (nullable, no default).
3. `ALTER TABLE orders ADD COLUMN status TEXT NOT NULL` (no default).
4. Drop the column `orders.legacy_ref`, which the **old** code still reads.
5. `CREATE INDEX idx_orders_created ON orders(created)` on a busy PostgreSQL table.
6. `UPDATE orders SET status = 'open' WHERE status IS NULL` for all 50 million rows in one statement.

Write your answer in `answer.md`. (The safe versions are in chapter sections 13.8 and 14.)
