# Monolith or services?

Chapter section 11 (monolith, modular monolith or microservices?) and "Try it: monolith or services?". For each of the three situations below, **choose a shape** (monolith, modular monolith, or services) and **defend it**: say what the reasons to split are in that case (or why there are none), what the split would cost, and what you would do **first**.

**A.** A team of 4 builds an online course platform: users, courses, video upload and transcoding, payments, e-mail. Daily traffic: 20,000 visits. Video transcoding takes 2 CPU-minutes per upload and spikes on Mondays.

**B.** A startup with 3 developers wants to start with microservices "because everybody does", with one service per table of its 12-table database.

**C.** A company of 120 developers in 14 teams has one large Django application. Releases happen once a month because every team must agree; one team's bug took the whole site down twice; the payments team needs an audited, isolated boundary for card data.

In `answer.md` write about 350 to 500 words, covering:

1. The **choice** for A, B and C, each in one sentence, and the main reason.
2. The **availability tax**: if one request needs 5 services that are each up 99.9% of the time, how often does the request succeed (say the percentage and about how many minutes a month that is)? What does it teach for case B?
3. The **good reasons to split** (give three, tied to people or load), and the **poor reasons** (give two).
4. What a **modular monolith** is (three properties) and why it is the usual first answer.
5. If a split is justified, **how** you would do it without a rewrite (the strangler fig), and one thing about the **event format** that you must treat as an API.

Use the words *independent deployment*, *Conway's law*, *distributed monolith*, *outbox*, *seam*.

## Example

A good line for part 2: "0.999^5 is about 99.5%: a monolith with one dependency fewer in the request path is more available than five services in a chain".
