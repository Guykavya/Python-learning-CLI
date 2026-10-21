**1. The three symptoms.**

- **Choice 1**: `show_balance` contains a typo, `balanse`, so it raises **`NameError`** every time
  it runs. The bare `except:` catches it and prints "Invalid input, try again". The user is blamed
  for a bug in the program, and the programmer never sees a traceback pointing at the typo.
- **Choice 3**: `sys.exit()` does not stop the program directly; it **raises `SystemExit`**, which
  is supposed to travel up and end the program. The bare `except:` catches it too, prints the
  message and the loop goes round again.
- **Ctrl+C**: pressing it raises **`KeyboardInterrupt`** in whatever line is running. If that line
  is inside the `try` (for example the `input("Amount: ")` in `deposit`), the bare `except:`
  catches it. (While waiting at the menu prompt, which is outside the `try`, Ctrl+C would still
  work. The symptom appears whenever the user presses it during an action.)

**2. except Exception.** `SystemExit` and `KeyboardInterrupt` inherit from `BaseException`
directly, **not** from `Exception`, precisely so that "catch all ordinary errors" does not stop a
program from being stopped. With `except Exception:`, quitting and Ctrl+C would work again. But
`NameError` **is** an `Exception`, so choice 1 would still print "Invalid input" and still hide the
typo.

**3. The rewrite.** The only expected failure from the user is typing something that is not a
whole number for the amount, which makes `int()` raise `ValueError`:

```python
def show_balance():
    print("Balance:", balance)          # typo fixed

while True:
    choice = input("1) balance  2) deposit  3) quit: ")
    if choice == "1":
        show_balance()
    elif choice == "2":
        try:
            deposit()
        except ValueError:
            print("The amount must be a whole number of rupees, for example 200.")
    elif choice == "3":
        sys.exit()
    else:
        print("Unknown choice. Type 1, 2 or 3.")
```

Now `sys.exit()` and Ctrl+C work, and if another bug like the typo appears, it crashes with a
traceback that names the line. (Even better, `deposit` could read the text and convert it in its
own narrow `try`, so a `ValueError` from somewhere else inside `deposit` could not be mistaken for
a bad amount.)

**4. The lesson.** "Never crashes" must mean "handles every **expected** failure from the world",
not "silences everything". A handler that catches bugs, exit requests and Ctrl+C makes the program
impossible to debug and impossible to stop; catch specific exceptions in narrow `try` blocks and
let bugs surface.

Key ideas to check: NameError from the typo; sys.exit raises SystemExit; Ctrl+C raises
KeyboardInterrupt; both are BaseException but not Exception; except Exception still hides
NameError; catch only ValueError around the conversion; the message tells the user what to type.
