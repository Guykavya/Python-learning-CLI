# Split a message into header and body

E-mails and HTTP messages have the same shape: some header lines `Key: value`, then **one
blank line**, then the body.

```text
From: ann@x.in
Subject: Meeting
Time: 10:30

Hi team,

see you at 10:30.
```

Write `split_message(lines)` in `solution.py`. It returns a tuple `(headers, body)`:

- `headers` is a **dict** built from the lines **before the first blank line**. Split each
  header line at the **first** `:`, and strip spaces from the key and the value.
- `body` is a **list** of all lines **after** that blank line, unchanged. The body may contain
  more blank lines; keep them. The separating blank line itself is in neither part.
- If there is no blank line, every line is a header and the body is `[]`.
- A blank line is a line that is empty after `.strip()`.

**Important:** `lines` may be a **generator**, which you can read only once. So you cannot
search for the blank line first and slice afterwards. Read it in one pass.

**Example**

```python
msg = ["From: ann@x.in", "Subject: Meeting", "Time: 10:30", "",
       "Hi team,", "", "see you at 10:30."]
split_message(msg)
# ({'From': 'ann@x.in', 'Subject': 'Meeting', 'Time': '10:30'},
#  ['Hi team,', '', 'see you at 10:30.'])
```
