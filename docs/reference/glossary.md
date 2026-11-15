# Glossary

| Term | Meaning |
|---|---|
| Idempotent | Doing it twice has the same effect as once (safe to retry). |
| Mutable / immutable | Can / cannot be changed in place (`list` vs `tuple`). |
| Hashable | Has a fixed hash, so it can be a dict key or set member. |
| Iterator / generator | Object that gives values one by one / a function that `yield`s them lazily. |
| Closure | A function that remembers variables from where it was defined. |
| Decorator | A function that takes a function and returns a changed one. |
| Context manager | Object for `with`: sets up and always cleans up. |
| Big-O | How cost grows with input size, ignoring constants. |
| Race condition | The result depends on timing between threads or processes. |
| Fixture / mock / fake | Test setup / test double that records calls / small working stand-in. |
| Overfitting | Model memorised the training data and does badly on new data. |
| Data leakage | Information from the test set (or the future) used while training. |
| Precision / recall | Of predicted positives how many are right / of real positives how many found. |
| p-value | Chance of data at least this extreme if there is no effect. Not the chance the effect is real. |
| Drift | Live data or behaviour moves away from the data the model was trained on. |
| Embedding | A vector of numbers that places similar meanings close together. |
| RAG | Retrieve relevant text first, then let the model answer using it. |
| Token | The unit of text a language model reads and is billed for. |
| p95 latency | 95% of requests are faster than this. |
| CI | Automatic build and tests on every push. |
