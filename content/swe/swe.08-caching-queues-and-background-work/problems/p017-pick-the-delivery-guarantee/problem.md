# Pick the delivery guarantee

Chapter sections 8.4 (delivery guarantees), 11.1 (duplicates are normal) and "Try it: pick the guarantee". A worker handles one job in three moments: **receive** it, do the **effect**, **ack** it. The process can die at any moment, and the broker only knows whether the ack arrived.

In `answer.md` explain (about 250 to 400 words):

1. **At-most-once** and **at-least-once**: where the ack goes in each, and what a crash **before** and **after** the effect does in each case (lost or duplicated). A small 2 x 2 table is a good way to show it.
2. Why **exactly-once delivery** cannot be built between a worker and an outside system such as an e-mail provider. What do people build instead, and what two ingredients does it need?
3. List four everyday reasons why a job runs twice in a system with at-least-once delivery, even without bugs.
4. Choose a guarantee for each job below, and say what you would add so the choice is safe:
   - (a) adding one to a page-view statistic;
   - (b) charging a customer's card for order 812;
   - (c) sending a password-reset e-mail;
   - (d) a nightly job that deletes sessions older than 30 days.

Use the words *ack*, *lease*, *idempotent*, *idempotency key*, *effectively once*.

## Example

A good row of the table: "ack after the work, crash after the effect: the job comes back and the effect happens **twice**."
