# Explain: which principle is broken?

The five SOLID principles, in one line each:

- **S** Single responsibility: one reason to change.
- **O** Open/closed: add behaviour by adding code, not by editing working code.
- **L** Liskov substitution: a subclass can be used wherever its parent is expected, without surprises.
- **I** Interface segregation: do not force users of a class to depend on methods they do not use.
- **D** Dependency inversion: depend on small abstractions (a parameter, a Protocol), not on concrete classes you create inside.

Below are six pieces of code or complaints. For **each**, say which principle (or principles)
it breaks, why in one sentence, and the **smallest fix** (a sentence or a few lines of code).
**One** of them breaks two principles.

```python
# 1  "Every time the PDF layout changes, or the e-mail provider changes, or the totals rule
#     changes, we edit this class."
class Report:
    def build(self): ...
    def save_pdf(self, path): ...
    def send_email(self, to): ...

# 2  "To support a new discount type I had to edit this function and re-test all the others."
def discount(kind, price):
    if kind == "student":
        return price * 0.9
    elif kind == "senior":
        return price * 0.8
    elif kind == "vip":
        return price * 0.7
    return price

# 3  "My code takes a Rectangle, sets width 5 and height 4, and expects area 20.
#     With a Square it gives 16."
class Rectangle:
    def __init__(self, w, h): self.width, self.height = w, h
class Square(Rectangle):
    def set_width(self, w): self.width = self.height = w

# 4  "A BasicPrinter has to implement scan() and fax(). It raises NotImplementedError,
#     and the office code that loops over all Machines crashes on it."
class Machine:
    def print(self, doc): ...
    def scan(self): ...
    def fax(self, doc): ...
class BasicPrinter(Machine):
    def scan(self): raise NotImplementedError
    def fax(self, doc): raise NotImplementedError

# 5  "I cannot test OrderService without a real MySQL server."
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase("prod-host")

# 6  "To test this I have to send a real SMS."
def send_alert(message):
    client = TwilioClient(SECRET_KEY)
    client.send("+100000000", message)
```

Write `answer.md`: one short paragraph or bullet per item (about 250 to 400 words in all).

**Example of the level of detail expected (a different snippet)**

> `class Logger: def log(self, m): ...; def parse_csv(self, f): ...` **S**: one class with two
> unrelated reasons to change. Fix: move `parse_csv` into its own function or class.
