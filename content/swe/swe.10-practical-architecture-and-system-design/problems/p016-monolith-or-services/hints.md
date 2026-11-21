## Hint 1

For each case ask the two questions of section 11.4: is the reason about **people or load** (independent deployment, very different scaling, different failure tolerance, a compliance boundary) or about fashion? And what does the network add (failures, latency, distributed transactions, pipelines to run)?

## Hint 2

For the availability tax compute `0.999 ** 5`, then multiply `(1 - that)` by the minutes in a month (`30 * 24 * 60`). For part 5, remember that the outbox row is the seam: what must a consumer be able to rely on in the payload?
