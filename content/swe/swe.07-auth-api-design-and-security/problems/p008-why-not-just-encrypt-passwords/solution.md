## Approach

Answer the five questions in order and keep each answer to two or three sentences. See `answer.md` for a model answer and a checklist.

The core sentence: **we never need the password, only to check it.** A system that can recover a password has to keep a key, and a key kept next to the data protects very little. A system that only stores a slow, salted hash has nothing worth stealing, apart from the work of guessing.

Example: with AES, one leaked server means 100,000 readable passwords. With a salted scrypt hash, the thief must run a slow guess for each password separately, and the weak passwords fall first, the strong ones may never.

## Complexity

Not applicable.

## Another way

State it as a table: *encrypt* (reversible, key needed, wrong tool) / *fast hash* (one-way, but cheap to guess) / *slow salted hash* (one-way, expensive to guess, the right tool) / *+ pepper* (extra layer, with a rotation cost). A table makes the five answers easy to compare.
