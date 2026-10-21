# Explain: the menu that will not quit

This menu program "never crashes":

```python
import sys

balance = 500

def show_balance():
    print("Balance:", balanse)

def deposit():
    global balance
    balance += int(input("Amount: "))

while True:
    choice = input("1) balance  2) deposit  3) quit: ")
    try:
        if choice == "1":
            show_balance()
        elif choice == "2":
            deposit()
        elif choice == "3":
            sys.exit()
        else:
            print("Unknown choice")
    except:
        print("Invalid input, try again")
```

Users report three strange things: choosing **1** always says "Invalid input, try again"; choosing
**3** does not quit; and pressing **Ctrl+C** does not stop the program either.

In `answer.md`:

1. Explain each of the three symptoms. Name the exception involved in each, and where it comes
   from.
2. Explain why `except Exception:` instead of the bare `except:` would fix two of the symptoms but
   not the third. Use the exception hierarchy.
3. Rewrite the `try` part so that it handles **only** what it should, with a helpful message, and
   the `NameError` bug becomes visible so it can be fixed. Fix that bug too.
4. In one or two sentences: what is the general lesson about "a program that never crashes"?
