# Explain: why `Stack(list)` is a leaky stack

This is the explain assessment of the module.

Ravi needs a stack for an undo feature: you may only **push** on top, **pop** from the top and
**peek** at the top. He saves time by inheriting from `list`:

```python
class Stack(list):
    def push(self, item):
        self.append(item)

    def peek(self):
        if not self:
            raise IndexError("peek from empty stack")
        return self[-1]

    def is_empty(self):
        return len(self) == 0


s = Stack()
s.push(1)
s.push(2)
s.push(3)
s.insert(0, 99)
s.sort()
s[0] = "x"
print(s, s.peek())
print(s.pop(0), s)
both = s + [7]
print(type(both).__name__, isinstance(s, list))
```

Output:

```text
['x', 2, 3, 99] 99
x [2, 3, 99]
list True
```

His team lead says: "This is not a stack. Use composition." Ravi answers: "But it works, and I
wrote only three methods!"

In `answer.md` (about 250 to 400 words, plus a short code block), explain:

1. **What leaks.** Which operations from the output above break the stack rule, and why do they
   exist on a `Stack` at all? Name at least four `list` methods or operations a stack user should not
   have.
2. **is-a vs has-a.** Inheritance promises "a `Stack` **is a** `list`: you may use it wherever a list
   is expected". Why is that promise false here? What does `isinstance(s, list)` being `True` tell
   other code?
3. **The fix.** Rewrite `Stack` with **composition**: the stack **has a** list in a "private"
   attribute and offers only `push`, `pop`, `peek`, `is_empty` and `size`. Show the code. `pop()` and
   `peek()` on an empty stack raise `IndexError` with a clear message.
4. **The cost.** What does Ravi lose by not inheriting (things that came "for free"), and why is that
   cost small? What does he gain, for example when he later wants to store the items differently?
5. **When inheritance is right.** Give one example where subclassing a built-in or another class is
   a good idea, and the test you use to decide.

## Example of the level of detail

"`s.insert(0, 99)` puts 99 at the **bottom** of the stack. A stack has no bottom access at all, but
`Stack` inherited `insert` from `list`, so every list method is part of its public interface." A good
answer goes on like this for each point.
