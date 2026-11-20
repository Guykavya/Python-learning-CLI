## Hint 1

Write the story as a list of steps first: who creates what, who attacks, and what do you look at **after** each attack? Which request tells you whether a write attack changed something, and who should send it?

## Hint 2

For every attack there are two things to check: the answer of the attacker's request, and the state of Asha's data afterwards (read it as Asha). Which of the five apps is only caught by the second check? And which app is only caught by a check that does *not* involve Ravi at all?

## Hint 3

```text
client = make_client()
Asha creates a note (stop with a problem if this fails); remember id and the text
Asha reads it: must be 200 with the same text           (else: owner cannot read)
Ravi and anonymous read it: status must be 401/404, body must not contain the text
Ravi PATCH: status 404; then Asha reads: text unchanged
Ravi DELETE: status 404; then Asha reads: still 200
Ravi lists: the text must not appear in the list
return the list of problems
```
