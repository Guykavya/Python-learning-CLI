**1. Problems.**

1. **Shared class attribute.** `students = []` lives on the class. Two `SchoolApp` objects (two
   branches) append to the same list, so every report shows everybody, and tests leak into each other.
2. **Bare `except:` that prints.** It hides *every* error: a missing file, a typo in the code, even
   `KeyboardInterrupt`. The app then runs with zero students and nobody knows why.
3. **Magic error value.** `fee` returns `-1` for an unknown kind. A caller who adds up fees silently
   subtracts 1 rupee instead of noticing a data error. An unknown kind should raise.
4. **Dicts of strings instead of objects.** A typo like `s["emial"]` is a `KeyError` at run time,
   `marks` is a string `"78;91"` that every method has to split, and nothing checks the data when it
   enters the system.
5. **`if`/`elif` on `kind`.** Every new kind (for example "sibling discount") means editing `fee`, and
   the same chain will soon be copied into other methods. That is what polymorphism replaces.
6. **One class, many jobs.** Loading CSV, storing students, fee rules, grading, printing and e-mailing
   all live in one class. A change to the e-mail text risks breaking the fee rules, and you cannot reuse
   the grading on a web page because `report` prints.
7. **Work in `__init__`.** Creating the object reads a file. You cannot build a `SchoolApp` in a test
   without a CSV file, and failures happen at a surprising moment.
8. **Hard-wired mail server.** `email_results` creates `smtplib.SMTP` itself, so it cannot be tested
   without a real server, and the connection is never closed.
9. **Fragile grading.** Empty marks give a `ZeroDivisionError`/`ValueError`; the split is done twice;
   `DEBUG` is a global switch on the class instead of proper logging.

**2. New design.**

```python
class SchoolError(Exception): ...
class LoadError(SchoolError): ...                 # raised from OSError / csv.Error
class InvalidStudent(SchoolError): ...            # bad row: line number + reason

class FeePolicy:                                  # base: one method to override
    def fee(self) -> int: ...
class RegularFee(FeePolicy): ...                  # 20000
class ScholarshipFee(FeePolicy): ...              # 5000
class StaffChildFee(FeePolicy): ...               # 0
FEE_POLICIES = {"regular": RegularFee, ...}       # unknown kind -> InvalidStudent

class Student:
    def __init__(self, name, email, policy: FeePolicy, marks: list[int]): ...
    @property
    def average(self) -> float: ...               # raises InvalidStudent if no marks
    @property
    def grade(self) -> str: ...
    @property
    def fee(self) -> int: return self.policy.fee()
    @classmethod
    def from_row(cls, row: dict) -> "Student": ...  # parses "78;91", picks the policy

class Roster:                                     # has a list of students (per object!)
    def add(self, student): ...
    def report_lines(self) -> list[str]: ...      # returns text, does not print

class CsvLoader:
    def load(self, path) -> Roster: ...           # raises LoadError from the OSError

class Mailer:                                     # wraps smtplib; a FakeMailer for tests
    def send(self, to, text): ...

class ResultsService:                             # has a Roster and a Mailer
    def __init__(self, roster, mailer): ...
    def email_results(self): ...
```

Each class has one job. `ResultsService` *has* a roster and a mailer (composition) and receives them
from outside. Fees are polymorphic: `student.fee` asks its policy object, no `if` chain.

**3. Inheritance or not.** Subclasses (`ScholarshipStudent(Student)`) are simple and read naturally.
But a student's kind can **change** (a scholarship is granted in March), and an object cannot change its
class; and fee rules may combine with other rules (a hostel plan) and explode into classes like
`ScholarshipHostelStudent`. A `FeePolicy` object that the student *has* can be swapped at run time and
combined freely. I choose composition with a policy object.

**4. Testing.**

```python
def test_grade_and_fee():
    s = Student("Asha", "a@x.in", ScholarshipFee(), [90, 94])
    assert s.grade == "A" and s.fee == 5000

def test_email_without_server():
    class FakeMailer:
        def __init__(self): self.sent = []
        def send(self, to, text): self.sent.append((to, text))
    roster = Roster(); roster.add(Student("Ben", "b@x.in", RegularFee(), [60]))
    fake = FakeMailer()
    ResultsService(roster, fake).email_results()
    assert fake.sent == [("b@x.in", "Grade: C")]
```

No file, no network: the objects are built directly and the mailer is a duck-typed fake.
