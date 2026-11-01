1. **S, single responsibility.** `Report` has three reasons to change: the report content
   (`build`), the file format (`save_pdf`) and the delivery (`send_email`). Smallest fix: keep
   `Report.build` and move saving and sending into separate functions or classes
   (`save_pdf(report, path)`, `send_report(report, to)`).

2. **O, open/closed.** Each new discount means editing a working function, which can break old
   branches. Fix: a dictionary of strategies, `DISCOUNTS = {"student": lambda p: p * 0.9, ...}`,
   and `DISCOUNTS.get(kind, lambda p: p)(price)`. A new type is one new entry (or a registered
   function), with no edit to the lookup code.

3. **L, Liskov substitution.** A `Square` changes the meaning of the `Rectangle` contract
   ("width and height are independent"), so code written for `Rectangle` breaks. Fix: do not make
   `Square` a subclass; use two separate classes (or one `Rectangle` and a helper
   `square(side)` that returns a `Rectangle(side, side)`), or make shapes immutable.

4. **I and L (two principles).** `Machine` is a fat interface: a `BasicPrinter` is forced to
   carry `scan` and `fax` it cannot do (**I**). Raising `NotImplementedError` in the subclass
   means it cannot replace a `Machine` safely (**L**). Fix: split into small interfaces
   (`Printer`, `Scanner`, `Fax`, for example as Protocols) and let each class provide only
   what it really does.

5. **D, dependency inversion.** `OrderService` builds its concrete database inside itself, so it
   is welded to MySQL. Fix: take it as a parameter, `def __init__(self, db): self.db = db`, and
   pass a fake in tests.

6. **D, dependency inversion.** The function creates the real SMS client. Fix: accept the
   client (or a `send` function) as a parameter, `def send_alert(message, client)`, and give a
   fake one in tests.
