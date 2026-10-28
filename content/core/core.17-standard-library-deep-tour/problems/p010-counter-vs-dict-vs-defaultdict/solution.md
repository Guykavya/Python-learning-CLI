## What a good answer contains

- **The bug** is the read `failed[user] >= 3`: on a defaultdict, `d[key]` for a missing key
  calls the factory and **stores** the result, so every user ends up as a key with 0. Fixes:
  `failed.get(user, 0)`, or use a `Counter`, whose missing-key read returns 0 without storing.
- **Missing keys:** dict → `KeyError`; defaultdict → stores and returns `factory()`; Counter → 0,
  nothing stored. `in` and `.get()` never store.
- **Choices:** counting and top-N → `Counter`; grouping into lists → `defaultdict(list)`; fixed
  configuration where typos must fail → plain `dict`; multiset comparison → `Counter` subtraction.
- **Return `dict(result)`** so callers get normal `KeyError` behaviour instead of a dict that
  silently grows.

See `answer.md` for a full model answer.

## Rate yourself

- Did you name the **exact line** that creates the keys, not just "defaultdict is the problem"?
- Did you say that `Counter` does **not** store on a read? This is the detail most answers miss.
- Did each choice in part 3 come with a reason, not just a name?
