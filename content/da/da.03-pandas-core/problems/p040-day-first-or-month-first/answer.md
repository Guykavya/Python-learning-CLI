## Model answer

1. **The danger.** `03/04/2024` is a valid date in both orders (3 April or 4 March), so nothing raises an error and nothing looks wrong: a wrong guess silently moves rows to a different month. pandas only notices a problem when a value is impossible in the guessed order: a column mixing `01/02/2024` with `13/02/2024` raises a `ValueError`, because 13 cannot be a month. A column where *every* row is valid in both readings gets parsed without any complaint, usually with the month first.

2. **How to decide.** *In the data:* look for values with a first part above 12 (`13/02/2024` must be day-first) or a second part above 12 (month-first); the largest value in each position tells you which one is the day. If dates are sorted by time, the position that changes slowest is the month. *Outside the data:* ask who made the file, or check the source system and the country or locale of the exporting program (India and Europe write day first, the US month first). If both orders appear, the file was merged from several sources and must be split before parsing.

3. **Make it visible and check it.** State the format: `pd.to_datetime(s, format="%d/%m/%Y")` (or `dayfirst=True`), never rely on the guess; write the assumption in a comment or docstring. Use `errors="coerce"` and **count the failures** (rows that were not missing before but are `NaT` now): impossible days like `31/02/2025` and the other order show up there. Finally check the range: all dates should fall inside the period the file covers.

**Checklist: your answer should mention**
- [ ] ambiguous: both readings are valid, so no error is raised
- [ ] mixed rows raise a `ValueError` (an impossible value such as day 13)
- [ ] state the format (`format=` or `dayfirst`) instead of guessing
- [ ] look for values above 12 to find which part is the day
- [ ] count failures with `errors="coerce"`
- [ ] check the date range afterwards
