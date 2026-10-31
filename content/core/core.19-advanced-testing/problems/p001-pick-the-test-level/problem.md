# Explain: pick the test level

Tests come in three common sizes:

| Level | What runs for real | What is usually faked | Speed |
|---|---|---|---|
| **Unit** | one function or class | everything it talks to | milliseconds |
| **Integration** | a few parts together (code + disk, code + parser + writer) | the outside world (network, payment, clock) | tens of ms to seconds |
| **End-to-end (e2e)** | the whole system the way a user uses it | almost nothing | seconds to minutes |

Below are six situations. For **each one** say which level fits best (unit, integration or
end-to-end), give a one-sentence reason, and say what you would fake or leave real.

1. `slugify("Hello World")` must return `"hello-world"`. You want to check twelve odd inputs
   (empty string, accents, repeated spaces).
2. `save_notes(path, notes)` writes a file and `load_notes(path)` reads it back. You want to know
   that what is saved can be loaded again.
3. `checkout(cart, gateway)` applies discounts and then calls `gateway.charge(amount)` on a
   payment service. You want to check **only** the discount rules.
4. A user opens the staging website in a real browser, adds a book to the cart, pays with a test
   card, and sees the "Thank you" page.
5. `main(["report", "sales.csv"])` is a command line tool: it reads the CSV, cleans the rows,
   adds up the totals and writes `report.txt`. You want to know the whole chain works.
6. Your nightly script depends on a weather web service returning `{"temp": <number>}`. You want
   to notice when the service changes its format.

Write `answer.md` (about 200 to 300 words). Finish with two sentences on why a healthy suite has
**many unit tests and few end-to-end tests** (the "test pyramid").

**Example of the level of detail expected for one line**

> 7. `is_even(4)` must be `True`: **unit**. One pure function, no outside parts, so nothing to
> fake and the test runs in microseconds.
