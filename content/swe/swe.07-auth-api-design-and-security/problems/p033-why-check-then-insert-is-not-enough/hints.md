## Hint 1

Put yourself in the client's place after a timeout. What exactly do you know? What are the two things that could have happened, and can you tell them apart? What do you do next, and what could that cost the customer?

## Hint 2

Draw the code above as a timeline for **two** requests with the same key (A and B), one line per statement: `SELECT`, `charge`, `INSERT`. Find an order of the six steps in which both A and B see "not found". Then draw one request and put a crash between `charge` and `INSERT`.

## Hint 3

```text
1. blind client      -> retry is necessary; a key makes it safe
2. key protocol      -> client sends key; server stores (user, key, fingerprint, response); repeat = same response
3. race              -> A: SELECT (none)  B: SELECT (none)  A: charge  B: charge  (two charges)
4. crash gap         -> charge done, process dies, no key stored, retry charges again
5. fix               -> INSERT the key first (unique constraint: one winner), do the work and mark "completed" in ONE transaction
```
