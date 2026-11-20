## Approach

The model answer is in `answer.md`. Everything rests on the 2 x 2 table: the position of the ack decides whether a crash **loses** or **duplicates**. Then: duplicates cannot be prevented in a distributed system, so make them harmless (idempotent handlers), and choose the guarantee per job by asking which failure costs more.

## Cost

At-least-once with idempotency costs a dedupe record or an idempotency key per effect, and a careful handler design (chapter 11). At-most-once costs nothing extra, but you must accept losses.

## Another way

Some brokers advertise "exactly-once" (Kafka transactions, SQS FIFO deduplication). Read the fine print: it covers moving messages *inside* that system (or within a time window). As soon as the effect is an e-mail, a payment or another company's API, you are back to at-least-once plus idempotency.
