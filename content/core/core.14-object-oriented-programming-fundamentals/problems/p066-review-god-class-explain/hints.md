## Hint 1

Read the class one method at a time and ask three questions: "Whose data is this, and who else can
change it?", "What happens when something goes wrong here?", and "Could I test this method on its own
in two lines?" Each "no" or "everybody" is a problem for your list.

## Hint 2

For the redesign, list the **jobs** first: read a CSV file, represent one student, decide a fee,
compute a grade, hold all students, format a report, send e-mail. Usually each job becomes one class
or one method on the right class. Then decide who *has* whom.

## Hint 3

Plan of the answer:

```text
1. problems: class-level list, bare except, -1, dicts of strings, if-chain on kind,
   one class many jobs, file read in __init__, SMTP created inside, marks as a string
2. classes: SchoolError > LoadError, InvalidStudent; FeePolicy + subclasses; Student (from_row
   classmethod, grade/fee properties); Roster; CsvLoader; Mailer; ResultsService(roster, mailer)
3. Student subclasses vs FeePolicy object: kinds change at run time, rules combine -> composition
4. tests: build Student objects directly; pass a FakeMailer with a send() method
```
