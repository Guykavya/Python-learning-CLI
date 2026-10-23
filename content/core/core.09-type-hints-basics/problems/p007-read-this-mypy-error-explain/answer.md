**1. Reading the line.** `orders.py:5` is the file and the line where mypy found the problem: the
call on line 5. `Argument 2` means the second argument in that call, counting from 1, so it is the
tax. `"str"` is the type that was actually given. `"float"` is the type the hint `tax: float`
demands. `[arg-type]` is the error code, the category "wrong argument type"; it stays the same
between mypy versions even when the wording changes.

**2. Where the mistake is.** In the call. The function is right: a tax rate is a number, so
`float` is the correct hint. I would pass `0.18` instead of `"0.18"`. If the text came from the
user, I would convert it first with `float(text)` inside a `try`.

**3. Running with Python.** The hint does not stop anything. Python runs the program until it
computes `1 + "0.18"`, where the `+` operator raises a `TypeError`. The message talks about adding
an int and a str, not about the hint. (If the body had only returned `tax`, there would be no error
at all.)

**4. Why mypy is still useful.** It found the bad call without running anything, and it points at
the exact line. Even if that call sat on a path that runs once a year, mypy would still report it,
while Python would only fail when a user reached that path.
