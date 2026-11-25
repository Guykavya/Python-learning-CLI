## Model answer

1. **Phone numbers fail as keys.**
   - The number **changes over time**: a new SIM, a new city. The same person then looks like two customers, and the
     old jobs are not joined to the new ones.
   - The number is **reused**: the operator gives an old number to a new person, who inherits a stranger's history.
   - The number is **not unique** in real life: a family or a small shop shares one phone, so one key stands for
     several customers.
   - Two systems write it differently (`+91 98765 43210`, `098765-43210`, `9876543210`), so a join loses rows
     unless the text is cleaned first, as in da.05.

2. **The surrogate key.** `customer_id` is arbitrary, assigned once and never reused, so it does not change when the
   person's details change. But it is **meaningless**: it will not tell you that two ids are the same person (a customer who
   registered twice), and it cannot be typed into another system's file without a mapping.

3. **Keep a uniqueness rule on the natural columns too.** If the phone number should identify a person, the table needs a
   unique constraint or a regular test on it; otherwise the surrogate key quietly allows the same person to be stored
   twice, and counts of customers are inflated. The surrogate key says "this row is unique", not "this person is
   unique".

**Checklist: your answer should mention**
- [ ] a natural key changes over time (or is reused)
- [ ] a natural key can be not unique (shared) or written in different formats
- [ ] a surrogate key is stable but meaningless (cannot spot duplicate people)
- [ ] keep a unique constraint or test on the natural columns too
