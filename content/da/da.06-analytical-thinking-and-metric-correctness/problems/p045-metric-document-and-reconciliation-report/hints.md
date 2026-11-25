## Hint 1

Split the project into small functions you can test one by one: a text formatter for the document, a function that
builds the steps of each bridge (and the job ids behind each line), and the `bridge` text formatter. Which of them
did you already write in this module? What must every bridge do before the report may print it? Which dates are the
boundary cases in the data, and which side of each boundary are they on?

## Hint 2

```text
definition_doc: header lines, then for each spec the seven lines (### name, five "- Field: value" lines, an empty line)
volume steps: T = created in [start, end); C = completed and started in [start, end)
              T-only jobs by status (cancelled / failed / pending / else "started after the month"), C-only = "created before..."
cash steps:   seven lines of "Cash against work" (before, after, not paid yet, earlier, later or pending, other, refunds)
bridge(start_label, start, steps, end_label, end): running total, ValueError when it does not reach the end
report = title, "## 1. ...", blank, bridge 1, blank, "Jobs behind each line:" + ids, blank, "## 2. ...", ...
ids: one "- label: [ids]" line for each step with jobs, in the order of the bridge; "- none" when no step has jobs
```
