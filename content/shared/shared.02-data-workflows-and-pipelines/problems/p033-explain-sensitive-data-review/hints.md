## Hint 1

Follow the data and the secret through the program and list every place they **land**: a
source file, a log file, a database file, a CSV file. For each place ask: who can read it, how long
does it stay there, and does that person or that time span actually need it? A problem is any
place where the answer to the last question is "no".

## Hint 2

```
secret   : in code / git? in logs? -> environment variable or secret store; rotate a leaked one
logs     : full records, headers, DEBUG in production? -> ids, counts, run id only
database : who can open the file? -> service account only (file permissions), views or files per role
           raw emails -> pseudonymise (HMAC) in clean tables
export   : what is the question? -> share only the answer (aggregates), not row-level PII
retention: kept "just in case"? -> a rule (delete raw after N days) that the job enforces
"not enough": sha256 of emails (dictionary attack), masking (still row-level), hidden folders (still readable)
```
