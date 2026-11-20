# Cache or queue?

Chapter section 1 ("Three problems, two tools") and "Try it: cache or queue?". A **cache** keeps a copy of an expensive answer so the next request is fast; it is right when the same read happens often and a little staleness is fine. A **queue** moves slow or unreliable work out of the request so a worker does it later; it is right when the user does not need the result *now*. Some situations need **both** (a background job produces something that is then served from a cache), and some need **neither** (the answer must be exact and current, or the user must see the outcome now).

For each situation write `cache`, `queue`, `both` or `neither`. No program is shown; this is a reading exercise.

1. A product page is built from 12 database queries and viewed 300 times a second. Prices change about once a day.
2. An editor presses "Send" on a newsletter that must go to 10,000 subscribers.
3. A monthly sales report takes 2 minutes to build. Once built, managers download it many times during the month.
4. At checkout, the shop checks whether a one-time coupon code has already been used.
5. A user uploads a profile photo, which must be resized into three sizes.
6. A sign-up form shows a drop-down list of the world's countries.
7. Before a cash withdrawal, the bank shows the customer's current balance.
8. Exchange rates come from an outside API that allows only 100 calls a day. Every product page shows prices in the visitor's currency. A job refreshes the rates every hour.

## Example

A situation like "a home page rebuilt from 20 queries, viewed 50 times a second, where a few seconds of staleness is fine" is `cache`.

## Answer format

Write exactly eight lines, one per situation, in this form (number, colon, space, one word):

```text
1: cache
2: queue
...
```

## After you answer

- For situation 4, what goes wrong if a cache says "not used yet" for 60 seconds?
- For situation 3, which part is the queue and which part is the cache?
