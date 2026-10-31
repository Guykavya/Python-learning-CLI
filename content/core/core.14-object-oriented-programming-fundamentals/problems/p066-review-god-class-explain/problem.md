# Explain: review a God class and redesign it

A **God class** knows and does everything. It works at first, then every change breaks something.
An intern wrote this for a coaching centre. Review it like a senior developer.

```python
import csv
import smtplib


class SchoolApp:
    students = []                      # all students of all SchoolApp objects
    DEBUG = True

    def __init__(self, csv_path, smtp_host):
        self.csv_path = csv_path
        self.smtp_host = smtp_host
        self.load()

    def load(self):
        try:
            with open(self.csv_path) as f:
                for row in csv.DictReader(f):
                    self.students.append(row)          # each row is a dict of strings
        except:
            print("could not load")

    def add_student(self, name, email, kind, marks):
        self.students.append({"name": name, "email": email, "kind": kind, "marks": marks})

    def fee(self, student):
        if student["kind"] == "regular":
            return 20000
        elif student["kind"] == "scholarship":
            return 5000
        elif student["kind"] == "staff_child":
            return 0
        else:
            return -1

    def grade(self, student):
        avg = sum(int(m) for m in student["marks"].split(";")) / len(student["marks"].split(";"))
        if avg >= 90: return "A"
        if avg >= 75: return "B"
        if avg >= 50: return "C"
        return "F"

    def report(self):
        for s in self.students:
            print(s["name"], self.grade(s), self.fee(s))

    def email_results(self):
        server = smtplib.SMTP(self.smtp_host)
        for s in self.students:
            if self.DEBUG:
                print("sending to", s["email"])
            server.sendmail("office@centre.in", s["email"], f"Grade: {self.grade(s)}")
```

In `answer.md` (about 400 to 600 words, plus a short sketch of the new classes), write:

1. **The problems.** List at least **seven** concrete problems in this code. For each, say which line
   or idea causes it and what can go wrong in practice. Think about: the class attribute, the bare
   `except`, `-1` as an error value, strings instead of objects, the `if`/`elif` chain on `kind`,
   mixing calculation with printing and emailing, work done in `__init__`, testing without a real
   mail server, and `marks` stored as a string.
2. **The new design.** Propose the classes (names and one-line responsibilities). Use **composition**
   (who *has* whom), **polymorphism** for the fee rules (instead of the `if` chain), a small
   **exception hierarchy** for loading and data errors, and say where you would use a property or a
   classmethod. A short Python sketch (class lines and method signatures, bodies may be `...`) is enough.
3. **Inheritance or not.** For the student kinds, would you use subclasses of `Student`, or a separate
   `FeePolicy` object that a student *has*? Give one argument for each and choose.
4. **Testing.** Show how your design lets you test `grade` and the fees without a CSV file and without
   sending real e-mail.

## Example of the level of detail

"`students = []` is a **class** attribute, so two `SchoolApp` objects for two branches share one list:
loading the second branch adds its students to the first branch's report." A good answer goes on like
this for each problem.
