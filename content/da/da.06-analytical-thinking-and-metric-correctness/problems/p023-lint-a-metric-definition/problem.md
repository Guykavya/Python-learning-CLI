# Lint a metric definition

Chapter sections 7.1, 7.4 and 8.2. A definition that leaves out an ingredient will be filled in differently by every
reader. A **linter** reads a definition and lists what is wrong with it, the way a spell checker lists typos. Write

`lint_definition(spec)`

`spec` is a dict that describes one metric. It may have these keys (all values are text):
`name`, `question`, `grain`, `numerator`, `denominator`, `date_basis`, `time_zone`, `period`, `exclusions`, `owner`, `version`.

Return a **list of messages** (strings, an empty list means the definition is clean). Check four things, and produce
the messages **in this order**:

1. **Missing fields.** For each of `name, question, grain, numerator, denominator, date_basis, period, exclusions, owner, version`
   (in this order) that is absent, `None`, or empty after `.strip()`: `"missing: <field>"`.
   (For a count that has no denominator, write `"-"`: that is an answer. An empty text is not.)
2. **Vague words.** For each of `numerator, denominator, exclusions` (in this order), and inside a field for each of the
   words `active`, `recent`, `valid` (in this order): if the text contains the word (any capitals) **and no rule**,
   the message is `"vague: <field> uses '<word>' without a rule"`. A text has a **rule** when it contains a digit or one
   of the characters `=`, `<`, `>`. So `"active customers"` is vague, and `"active = a job created in the last 90 days"` is not.
3. **Closed interval.** If `period` is present and either contains the word `between` (any capitals) or has `<=` followed
   by a date or number (a digit after optional spaces and an optional quote), the message is
   `"closed interval: write the period as start <= t < end"`. The text `">= 2025-02-01 and < 2025-03-01"` is fine.
4. **Time zone.** A time zone is given when `time_zone` is not empty, **or** `date_basis` contains `UTC` or `IST`.
   Otherwise: `"no time zone: say UTC or IST"`.

Do not change `spec`.

## Example

```python
spec = {"name": "jobs_completed", "question": "how much work was finished?", "grain": "job",
        "numerator": "valid completed jobs", "denominator": "-", "date_basis": "completed_at",
        "period": "created_at between '2025-02-01' and '2025-02-28'", "exclusions": "none", "owner": "", "version": "v1"}
for message in lint_definition(spec):
    print(message)
```

```text
missing: owner
vague: numerator uses 'valid' without a rule
closed interval: write the period as start <= t < end
no time zone: say UTC or IST
```
