# dsa.08 Stacks and queues

## 1. Two rules for order

Think of two lines of people.

At a ticket counter, the person who arrived **first** is served first. New people join at the back. This is a **queue**: first in, first out (**FIFO**).

Now think of a pile of plates in a canteen. You put a clean plate on top, and you take a plate from the top. The plate you put **last** is the one you take **first**. This is a **stack**: last in, first out (**LIFO**).

That is the whole difference: *which element do I take next?* A queue gives you the oldest one. A stack gives you the newest one. It sounds too simple to be a big topic, but this one choice solves a surprising number of problems, and some of them look hard until you see
the stack hiding inside.

Where do you meet them?

- **Stack:** the undo button in an editor (the last change is undone first), the back button of a browser, the call stack of your own recursive functions (dsa.07), matching brackets in code, evaluating `3 + 4 * 2`.
- **Queue:** print jobs, customers waiting for support, tasks waiting for a worker, and **BFS** (breadth-first search), which you will use on graphs and grids in later modules.
- **Both ends at once (a deque):** a sliding window over a list, the "last 10 items" view, a palindrome check from both sides.

### What you can do after this module

1. **Use a list as a stack and `collections.deque` as a queue**, and say why a plain list is the wrong queue.
2. **Solve the classic stack problems**: balanced brackets, evaluating expressions, simplifying paths, decoding nested strings.
3. **Design with two structures**: a stack that knows its minimum in `O(1)`, a queue built from two stacks.
4. **Recognise "next greater element" problems** and solve them in `O(n)` with a **monotonic stack**: daily temperatures, stock span, largest rectangle in a histogram.
5. **Use a monotonic queue** for the maximum of every sliding window.
6. **Run a queue-based simulation or BFS**, such as a hot-potato game or the spread of rotting oranges on a grid.

### A first look

A list works as a stack, because `append` and `pop` both work on the right end. A `deque` works as a queue, because `append` adds at the right and `popleft` takes from the left.

```python
from collections import deque

stack = []
for item in "abc":
    stack.append(item)          # push
print(stack.pop(), stack.pop(), stack)

queue = deque()
for item in "abc":
    queue.append(item)          # enqueue
print(queue.popleft(), queue.popleft(), queue)
```
```text
c b ['a']
a b deque(['c'])
```

Both received `a`, `b`, `c` in that order. The stack gave back `c` then `b` (the newest first). The queue gave back `a` then `b` (the oldest first).

**Predict the output 1.** Push 1, 2, 3 onto a stack, pop once, push 4, pop twice. What is left, and what did the pops return?

```python
stack = []
out = []
stack.append(1)
stack.append(2)
stack.append(3)
out.append(stack.pop())
stack.append(4)
out.append(stack.pop())
out.append(stack.pop())
print(out, stack)
```

<details><summary>Answer</summary>

```text
[3, 4, 2] [1]
```

The pops returned 3, then 4 (the new top), then 2. Only `1` remains, at the bottom. Draw the stack after each step if this surprised you: `[1,2,3]` -> pop 3 -> `[1,2]` -> push 4 -> `[1,2,4]` -> pop 4 -> pop 2 -> `[1]`.

</details>

## 2. A stack with a Python list

### The operations

A stack needs only a few operations, and a Python `list` does all of them in constant time.

| Stack operation | With a list `s` | Cost |
|---|---|---|
| push `x` | `s.append(x)` | `O(1)` amortised |
| pop (remove and return the top) | `s.pop()` | `O(1)` |
| peek (look at the top, do not remove) | `s[-1]` | `O(1)` |
| is it empty? | `not s` | `O(1)` |
| size | `len(s)` | `O(1)` |

"Amortised" means: one `append` occasionally has to grow the list's hidden storage, which costs more, but spread over many appends the average is constant. You can treat `append` as `O(1)`.

The **top** of the stack is the *right end* of the list. Always use the right end: `append` and `pop()` at the right are fast. Using the left end (`insert(0, x)` and `pop(0)`) shifts every element and costs `O(n)`.

### The empty-stack trap

Calling `pop()` or reading `s[-1]` on an empty list raises `IndexError`. This is the most common stack bug. **Ask `if s:` before you pop or peek**, unless you know the stack cannot be empty.

```python
s = []
try:
    s.pop()
except IndexError as e:
    print("pop:", e)

try:
    s[-1]
except IndexError as e:
    print("peek:", e)

print("empty?", not s)
```
```text
pop: pop from empty list
peek: list index out of range
empty? True
```

### A small `Stack` class

For clear code in big programs, wrap the list. This also lets you choose a better error message. In interviews and contests you will usually use the bare list, but the class shows what the operations *mean*.

```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, x):
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items})"


s = Stack()
s.push(10)
s.push(20)
print(s, s.peek(), len(s))
print(s.pop(), s.pop())
try:
    s.pop()
except IndexError as e:
    print("error:", e)
```
```text
Stack([10, 20]) 20 2
20 10
error: pop from empty stack
```

Because the class defines `__len__`, `if s:` also works: an object with `len() == 0` is falsy.

### Why a stack? Remember "the most recent unfinished thing"

A stack is the right tool whenever the thing you must handle next is **the most recent thing you started and have not finished yet**. Look at this sentence:

`(a [b {c} d] e)`

When you read the final `)`, which opener does it close? The *latest still-open* one, not the first. That is "most recent unfinished", and it is a stack. The same pattern appears in nested function calls, nested folders, nested HTML tags, and nested parentheses in a formula.

### Reversing with a stack

Pushing everything and then popping everything reverses the order. This is not the best way to reverse a string in Python (slicing does it), but it shows what a stack does to order.

```python
def reverse_with_stack(text):
    stack = []
    for ch in text:
        stack.append(ch)
    out = []
    while stack:
        out.append(stack.pop())
    return "".join(out)

print(reverse_with_stack("stack"))
print("stack"[::-1])
```
```text
kcats
kcats
```

### The recursion link

In dsa.07 you saw that recursion uses the **call stack**: each waiting call is an entry on a stack. You can always replace a recursive function by a loop and a stack of your own (section 15 of dsa.07). So stacks are not a new idea for you; they are the idea
behind recursion made visible.

**Try it 1.** Write `pop_n(stack, n)` that removes and returns the top `n` elements as a list (the first one popped comes first). If the stack has fewer than `n` elements, return only what exists, without an error.

<details><summary>Answer</summary>

```python
def pop_n(stack, n):
    out = []
    while stack and len(out) < n:
        out.append(stack.pop())
    return out

s = [1, 2, 3, 4, 5]
print(pop_n(s, 2), s)
print(pop_n(s, 10), s)
```
```text
[5, 4] [1, 2, 3]
[3, 2, 1] []
```

The loop condition checks `stack` (not empty) **before** each pop, which is exactly the guard from the trap above. The second call asks for 10 and gets only the 3 that were left.

</details>

## 3. A queue with `collections.deque`

### Why not a list?

A queue takes from the **front** (the oldest). With a list, the front is index 0, and `pop(0)` removes it. But a list stores its elements in one block of memory, so removing the first element means **moving every other element one place to the left**. That costs `O(n)`
for each removal.

Draining a queue of `n` items with `pop(0)` therefore costs `O(n^2)`. Let us measure it. (Only the yes/no comparisons are printed, because the exact times depend on your computer.)

```python
import time
from collections import deque

def drain_list(n):
    data = list(range(n))
    start = time.perf_counter()
    while data:
        data.pop(0)
    return time.perf_counter() - start

def drain_deque(n):
    data = deque(range(n))
    start = time.perf_counter()
    while data:
        data.popleft()
    return time.perf_counter() - start

n = 30_000
slow = drain_list(n)
fast = drain_deque(n)
print("list.pop(0) is slower than deque.popleft():", slow > fast)
print("more than 5 times slower:", slow / fast > 5)
```
```text
list.pop(0) is slower than deque.popleft(): True
more than 5 times slower: True
```

The gap grows as `n` grows, because one side is quadratic and the other is linear. A `deque` (pronounced "deck", short for *double-ended queue*) stores its items in linked blocks, so adding or removing at **either end** costs `O(1)`. For a queue, always use `deque`.

### The deque operations

| Operation | Code | Cost |
|---|---|---|
| enqueue at the back | `d.append(x)` | `O(1)` |
| dequeue from the front | `d.popleft()` | `O(1)` |
| add at the front | `d.appendleft(x)` | `O(1)` |
| remove from the back | `d.pop()` | `O(1)` |
| look at the front / back | `d[0]` / `d[-1]` | `O(1)` |
| size | `len(d)` | `O(1)` |
| index in the middle | `d[i]` | `O(n)` for a middle `i` |
| rotate | `d.rotate(k)` | `O(k)` |

The last two lines are the catch. A deque is great at the ends and poor in the middle: `d[len(d) // 2]` walks through the blocks. If you need random access, use a list; if you need both ends, use a deque.

```python
from collections import deque

d = deque([1, 2, 3])
d.append(4)
d.appendleft(0)
print(d)
print(d.popleft(), d.pop(), d)
d.extend([7, 8])
d.extendleft([-1, -2])         # each item goes to the front, one by one
print(d)
d.rotate(2)                    # move 2 items from the right end to the left end
print(d)
d.rotate(-1)                   # move 1 item from the left end to the right end
print(d)
```
```text
deque([0, 1, 2, 3, 4])
0 4 deque([1, 2, 3])
deque([-2, -1, 1, 2, 3, 7, 8])
deque([7, 8, -2, -1, 1, 2, 3])
deque([8, -2, -1, 1, 2, 3, 7])
```

Look at `extendleft([-1, -2])`: it adds `-1` first and then `-2`, each time at the front. So the order is *reversed* in the deque (`-2, -1, ...`). That surprises many people.

### `maxlen`: a queue that forgets old items

`deque(maxlen=k)` keeps at most `k` items. When it is full and you append, the item at the opposite end is dropped for you. It is a ready-made "last `k` things" container.

```python
from collections import deque

last3 = deque(maxlen=3)
for x in [10, 20, 30, 40, 50]:
    last3.append(x)
    print(list(last3), "sum =", sum(last3))
```
```text
[10] sum = 10
[10, 20] sum = 30
[10, 20, 30] sum = 60
[20, 30, 40] sum = 90
[30, 40, 50] sum = 120
```

### A queue class

```python
from collections import deque

class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, x):
        self._items.append(x)

    def dequeue(self):
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def front(self):
        if not self._items:
            raise IndexError("front of empty queue")
        return self._items[0]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Queue({list(self._items)})"

q = Queue()
for name in ("Asha", "Ben", "Chitra"):
    q.enqueue(name)
print(q, q.front())
print(q.dequeue(), q.dequeue(), q)
```
```text
Queue(['Asha', 'Ben', 'Chitra']) Asha
Asha Ben Queue(['Chitra'])
```

### Looking inside: a queue built on a fixed array (a ring buffer)

How can a queue be fast with only a plain list? The trick is to **not move the elements**. Keep a fixed-size array, and two numbers: `head` (where the oldest element is) and `size` (how many elements there are). A new element goes to position `(head + size) % capacity`, and when it passes the end of
the array, it wraps around to the start, like a ring. Removing only moves `head` forward by one (again with `% capacity`). Nothing is shifted.

```python
class RingQueue:
    def __init__(self, capacity):
        self._data = [None] * capacity
        self._head = 0
        self._size = 0

    def __len__(self):
        return self._size

    def enqueue(self, x):
        if self._size == len(self._data):
            raise OverflowError("queue is full")
        tail = (self._head + self._size) % len(self._data)
        self._data[tail] = x
        self._size += 1

    def dequeue(self):
        if self._size == 0:
            raise IndexError("dequeue from empty queue")
        x = self._data[self._head]
        self._data[self._head] = None
        self._head = (self._head + 1) % len(self._data)
        self._size -= 1
        return x

q = RingQueue(3)
for x in (1, 2, 3):
    q.enqueue(x)
print(q._data, "head =", q._head)
print(q.dequeue())
q.enqueue(4)                           # wraps around to index 0
print(q._data, "head =", q._head, "size =", len(q))
try:
    q.enqueue(5)
except OverflowError as e:
    print("error:", e)
```
```text
[1, 2, 3] head = 0
1
[4, 2, 3] head = 1 size = 3
error: queue is full
```

After the dequeue of `1`, the first slot is free, and `4` is stored there. The queue's order is still `2, 3, 4`: it starts at `head = 1` and wraps around. You do not need to write this in your solutions (use `deque`), but it explains why a queue can be `O(1)` at both ends, and it is a common exam question.

### Other queues in the standard library

- `queue.Queue` is a queue for **threads** (core.21): it locks, and `get()` can wait for an item. It is slower than `deque`, so do not use it for algorithms.
- `heapq` and `queue.PriorityQueue` give a *priority* queue: the next item out is the smallest, not the oldest. That is a different structure (a heap), used for Dijkstra and for "k largest" problems.

**Predict the output 2.** What does this print?

```python
from collections import deque

d = deque([1, 2, 3, 4, 5])
d.rotate(2)
d.appendleft(d.pop())
print(list(d))
```

<details><summary>Answer</summary>

```text
[3, 4, 5, 1, 2]
```

`rotate(2)` moves the last two items to the front: `[4, 5, 1, 2, 3]`. Then `d.pop()` takes the `3` from the right end and `appendleft` puts it at the front: `[3, 4, 5, 1, 2]`. Notice that `d.appendleft(d.pop())` is the same as `d.rotate(1)`.

</details>

## 4. The deque at both ends

Because a deque is fast at both ends, it can be a stack (use `append` and `pop`), a queue (`append` and `popleft`), or something that uses both ends at once. Here are three jobs where both ends matter.

### Palindrome check from both sides

Compare the first and last items, remove both, and repeat until zero or one item is left.

```python
from collections import deque

def is_palindrome(text):
    d = deque(ch.lower() for ch in text if ch.isalnum())
    while len(d) > 1:
        if d.popleft() != d.pop():
            return False
    return True

print(is_palindrome("A man, a plan, a canal: Panama"))
print(is_palindrome("hello"))
print(is_palindrome(""))
```
```text
True
False
True
```

The loop stops at `len(d) > 1`, so an odd-length string leaves its middle character untouched, and the empty string is a palindrome (nothing can be different).

### A moving time window: recent calls

A common design problem: "count how many requests arrived in the last 3000 milliseconds". Requests come in time order, so the oldest are at the **front**. Add each new time at the back; remove old times from the front.

```python
from collections import deque

class RecentCounter:
    def __init__(self, window=3000):
        self.window = window
        self.times = deque()

    def ping(self, t):
        self.times.append(t)
        while self.times[0] < t - self.window:
            self.times.popleft()
        return len(self.times)

c = RecentCounter()
for t in (1, 100, 3001, 3002, 6500):
    print(t, c.ping(t))
```
```text
1 1
100 2
3001 3
3002 3
6500 1
```

Check the third line by hand: at `t = 3001` the window is `[1, 3001]`, so both `1` and `100` are inside, and the count is 3. At `3002` the window starts at 2, so `1` falls out. Each time is appended once and removed at most once, so any number of pings costs `O(1)` each on average. The same shape ("add new on one side, drop old
on the other") is the base of every sliding window.

### The average of the last k values

```python
from collections import deque

class MovingAverage:
    def __init__(self, k):
        self.window = deque(maxlen=k)
        self.total = 0

    def next(self, x):
        if len(self.window) == self.window.maxlen:
            self.total -= self.window[0]        # the item about to be dropped
        self.window.append(x)
        self.total += x
        return self.total / len(self.window)

m = MovingAverage(3)
print([round(m.next(x), 2) for x in (1, 10, 3, 5)])
```
```text
[1.0, 5.5, 4.67, 6.0]
```

We keep a running `total` instead of calling `sum(window)` each time, which would cost `O(k)` per update. Notice the order inside `next`: we must subtract the oldest value **before** the `append` pushes it out. If you append first, the old value is already gone and you can no longer subtract it.

### Which one should I use?

| I need ... | Use |
|---|---|
| a stack (LIFO) | a `list` (`append`, `pop()`) |
| a queue (FIFO) | a `deque` (`append`, `popleft()`) |
| both ends, or "last k" with `maxlen` | a `deque` |
| fast access by index in the middle | a `list`, not a deque |
| the smallest (or largest) next | a heap (`heapq`) |

**Try it 2.** A deque holds the last 3 words typed. Write a function `last_words(words, k)` that returns the final `k` words of a long stream, using a `deque` with `maxlen`, and never builds a list of the whole stream.

<details><summary>Answer</summary>

```python
from collections import deque

def last_words(stream, k):
    window = deque(maxlen=k)
    for w in stream:
        window.append(w)
    return list(window)

def endless_words():
    n = 0
    while n < 1_000_000:
        yield f"w{n}"
        n += 1

print(last_words(endless_words(), 3))
print(last_words(iter(["a", "b"]), 5))
```
```text
['w999997', 'w999998', 'w999999']
['a', 'b']
```

Memory use is `O(k)`, whatever the length of the stream. When the stream has fewer than `k` items, the deque simply holds fewer. `maxlen` does the "forget the oldest" work for you.

</details>

## 5. Balanced brackets

The classic first stack problem. A string of brackets such as `([]{})` is **balanced** if every opening bracket is closed by the matching closing bracket, in the right order. `(]` is wrong (wrong type), `(()` is wrong (one never closed), and `)(` is wrong (a closer before any opener).

### The idea

Scan from left to right.

- At an **opening** bracket, you now owe a closer. Push the opener.
- At a **closing** bracket, it must close the *most recent* unclosed opener, which is the top of the stack. Pop it and check that the pair matches.
- At the end, the stack must be **empty**: no opener may be left waiting.

```python
PAIRS = {")": "(", "]": "[", "}": "{"}

def is_balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack

for s in ["([]{})", "(]", "((", ")(", "", "a(b[c]d)e"]:
    print(repr(s), is_balanced(s))
```
```text
'([]{})' True
'(]' False
'((' False
')(' False
'' True
'a(b[c]d)e' True
```

Every `False` has one of **three causes**, and the code handles each:

1. `(]`: the closer does not match the top. `stack.pop() != PAIRS[ch]`.
2. `)(`: a closer arrives and the stack is empty. `not stack` (and because of `or`, we do not pop from an empty list).
3. `((`: the scan ends with openers still waiting. `return not stack`.

If you forget the third check you accept `((`. If you forget the `not stack` guard, the empty-stack `pop()` crashes with `IndexError`. These are the two usual bugs; both are in the tests of this module.

Other characters (letters, spaces) are ignored, because we only react to brackets.

### Where exactly is the error?

Instead of `True/False`, we can report the position of the problem. Store the **index** with each opener.

```python
PAIRS = {")": "(", "]": "[", "}": "{"}

def first_error(text):
    """Index of the first problem, or -1 if the text is balanced.
    For an opener that is never closed, we report the earliest such opener."""
    stack = []                                   # holds (bracket, index)
    for i, ch in enumerate(text):
        if ch in "([{":
            stack.append((ch, i))
        elif ch in PAIRS:
            if not stack or stack[-1][0] != PAIRS[ch]:
                return i                         # a closer that closes nothing right
            stack.pop()
    return stack[0][1] if stack else -1

for s in ["([]{})", "(]", "((", ")(", "{[()]"]:
    print(repr(s), first_error(s))
```
```text
'([]{})' -1
'(]' 1
'((' 0
')(' 0
'{[()]' 0
```

### Three variants worth knowing

**Variant 1: only one kind of bracket.** If there is only `(` and `)`, you do not need a stack: a single counter of "open so far" is enough. The stack is needed only when there are different kinds, because then you must remember *which* kind is waiting.

```python
def min_additions(text):
    """Minimum number of brackets to add to make a ()-string balanced."""
    open_count = 0
    added = 0
    for ch in text:
        if ch == "(":
            open_count += 1
        elif ch == ")":
            if open_count:
                open_count -= 1
            else:
                added += 1            # a closer with nothing to close: add an opener
    return added + open_count          # plus one closer for each opener still waiting

print(min_additions("())"), min_additions("((("), min_additions("()))(("), min_additions("()"))
```
```text
1 3 4 0
```

**Variant 2: remove the fewest brackets to make the string valid.** The stack stores the **indices** of the openers, so that at the end we know exactly which characters to throw away.

```python
def min_remove_to_make_valid(s):
    drop = set()
    stack = []                                   # indices of unmatched "("
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if stack:
                stack.pop()                      # matched with the latest "("
            else:
                drop.add(i)                      # nothing to match: remove this ")"
    drop.update(stack)                           # every "(" still waiting must go
    return "".join(ch for i, ch in enumerate(s) if i not in drop)

for s in ["lee(t(c)o)de)", "a)b(c)d", "))((", "(a(b(c)d)"]:
    print(repr(s), "->", repr(min_remove_to_make_valid(s)))
```
```text
'lee(t(c)o)de)' -> 'lee(t(c)o)de'
'a)b(c)d' -> 'ab(c)d'
'))((' -> ''
'(a(b(c)d)' -> 'a(b(c)d)'
```

**Variant 3: the longest valid substring.** The stack holds indices, with a **sentinel** `-1` at the bottom that means "the last position before the current valid run". When we pop a matching opener, the length of the valid run ending here is `i - stack[-1]`, the distance to whatever is now on top.

```python
def longest_valid_parentheses(s):
    stack = [-1]                       # sentinel: index just before the current run
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:              # this ")" has no opener: it becomes the new sentinel
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return best

for s in ["(()", ")()())", "()(())", "", "))))"]:
    print(repr(s), longest_valid_parentheses(s))
```
```text
'(()' 2
')()())' 4
'()(())' 6
'' 0
'))))' 0
```

The sentinel is a useful trick: it avoids a special case for "the stack became empty". Trace `")()())"` (the answer is 4, the middle `()()`):

| index | char | action | stack after | best |
|---|---|---|---|---|
| start | | | `[-1]` | 0 |
| 0 | `)` | pop `-1`; stack empty, so push 0 (new sentinel) | `[0]` | 0 |
| 1 | `(` | push 1 | `[0, 1]` | 0 |
| 2 | `)` | pop 1; length `2 - 0 = 2` | `[0]` | 2 |
| 3 | `(` | push 3 | `[0, 3]` | 2 |
| 4 | `)` | pop 3; length `4 - 0 = 4` | `[0]` | 4 |
| 5 | `)` | pop 0; stack empty, so push 5 | `[5]` | 4 |

**Predict the output 3.** What is printed for each string?

```python
PAIRS = {")": "(", "]": "[", "}": "{"}

def is_balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack

print(is_balanced("[(])"), is_balanced("{[()()]}"), is_balanced("(()"))
```

<details><summary>Answer</summary>

```text
False True False
```

`[(])`: after `[` and `(`, the `]` arrives, but the top is `(`, so the pair does not match: `False`. The counts are right (one of each kind) and it is still wrong, because *order* matters. `{[()()]}` is fine. `(()` leaves one opener waiting.

</details>

## 6. Evaluating expressions

How does a program know that `3 + 4 * 2` is 11 and not 14? Multiplication binds tighter than addition: it is done first. Computers solve this with a stack. There are two steps: write the expression in a form without precedence rules, and evaluate that form with a stack.

### Postfix (reverse Polish notation)

In normal (**infix**) writing the operator sits between its numbers: `3 + 4`. In **postfix** it comes after: `3 4 +`. Postfix needs no brackets and no precedence rules, because the order of the tokens *is* the order of the work. `3 + 4 * 2` becomes `3 4 2 * +`: multiply 4 and 2, then add 3.

Evaluating postfix is a stack in its purest form:

- A **number**: push it.
- An **operator**: pop two numbers, apply the operator, push the result.

At the end, one number is left: the answer.

```python
def trunc_div(a, b):
    """Integer division that rounds toward zero (like C), not toward minus infinity."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q

def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b = stack.pop()                 # the second operand comes off first
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(trunc_div(a, b))
        else:
            stack.append(int(t))
    return stack[0]

print(eval_rpn("3 4 2 * +".split()))
print(eval_rpn("2 1 + 3 *".split()))
print(eval_rpn("4 13 5 / +".split()))
print(eval_rpn("10 6 9 3 + -11 * / * 17 + 5 +".split()))
```
```text
11
9
6
22
```

Two details decide whether your code is right:

1. **Operand order.** The first pop is `b` (the right operand), the second is `a`. For `-` and `/` the order matters: `8 3 -` is 5, not -5.
2. **Division.** Python's `//` rounds toward minus infinity, so `-7 // 2` is `-4`. Most languages (and most problems) say "truncate toward zero", which gives `-3`. Writing `int(a / b)` also truncates, but it goes through floats and can be wrong for very large numbers. The helper `trunc_div` stays in integers.

```python
print(-7 // 2, int(-7 / 2), (-7) % 2)
```
```text
-4 -3 1
```

### From infix to postfix: the shunting-yard method

We want to take `3 + 4 * 2 / ( 1 - 5 )` and produce the postfix form. We use a second stack for **operators** that wait for their turn.

For each token:

- **number**: output it at once;
- **operator**: while the operator on top of the stack has **higher or equal precedence**, move it to the output; then push the new operator;
- **`(`**: push it;
- **`)`**: move operators to the output until the matching `(`; throw the `(` away.

At the end, move all remaining operators to the output.

```python
import re

PREC = {"+": 1, "-": 1, "*": 2, "/": 2}

def tokenize(text):
    return re.findall(r"\d+|[-+*/()]", text)

def to_postfix(tokens):
    out, ops = [], []
    for t in tokens:
        if t.isdigit():
            out.append(t)
        elif t in PREC:
            while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[t]:
                out.append(ops.pop())
            ops.append(t)
        elif t == "(":
            ops.append(t)
        else:                                  # ")"
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()                          # discard the "("
    while ops:
        out.append(ops.pop())
    return out

for text in ["3 + 4 * 2", "(3 + 4) * 2", "3 + 4 * 2 / (1 - 5)", "8 - 3 - 2"]:
    postfix = to_postfix(tokenize(text))
    print(f"{text:22} -> {' '.join(postfix):18} = {eval_rpn(postfix)}")
```
```text
3 + 4 * 2              -> 3 4 2 * +          = 11
(3 + 4) * 2            -> 3 4 + 2 *          = 14
3 + 4 * 2 / (1 - 5)    -> 3 4 2 * 1 5 - / +  = 1
8 - 3 - 2              -> 8 3 - 2 -          = 3
```

(This block uses `eval_rpn` and `trunc_div` from the blocks above. In a real file you would put all the functions together.)

Look at `8 - 3 - 2`. The answer must be `3`, not `7`: subtraction is **left to right**. That is why the comparison uses `>=` (pop an operator of *equal* precedence before pushing the new one). With `>` the new `-` would not push the old `-` out, and the postfix form would
be `8 3 2 - -`, which means `8 - (3 - 2) = 7`. A one-character bug.

### Evaluate with a single pass (no postfix)

Often you do not need the postfix form at all. Here are two more direct calculators.

**Calculator 1: `+`, `-` and parentheses.** Keep a running `result` and a `sign` for the next number. A `(` starts a new sub-expression: save the current `result` and `sign` on the stack and start fresh. A `)` ends it: compute its value and combine it with what was saved.

```python
def calculate(s):
    stack = []
    result = 0
    number = 0
    sign = 1
    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch in "+-":
            result += sign * number
            number = 0
            sign = 1 if ch == "+" else -1
        elif ch == "(":
            stack.append(result)
            stack.append(sign)
            result, sign = 0, 1
        elif ch == ")":
            result += sign * number
            number = 0
            result *= stack.pop()          # the sign saved before "("
            result += stack.pop()          # the result saved before "("
    return result + sign * number

for s in ["1 + 1", " 2-1 + 2 ", "(1+(4+5+2)-3)+(6+8)", "-(2+3)", "10-(2-5)"]:
    print(repr(s), calculate(s))
```
```text
'1 + 1' 2
' 2-1 + 2 ' 3
'(1+(4+5+2)-3)+(6+8)' 23
'-(2+3)' -5
'10-(2-5)' 13
```

For `10-(2-5)`: the `-` sets `sign = -1`. At `(` we save `result = 10` and `sign = -1`, then restart at `result = 0, sign = 1`. Inside: `2 - 5 = -3`. At `)` we multiply by the saved sign: `-3 * -1 = 3`, then add the saved `10`: `13`.

**Calculator 2: `+`, `-`, `*`, `/`, no parentheses.** Idea: addition and subtraction can wait, but a `*` or `/` must act on the **last term immediately**. So keep a stack of terms. A `+` pushes the number, a `-` pushes its negative, and a `*` or `/` changes the number on top. At the end, the sum of the stack is the answer.

```python
def trunc_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q

def calculate2(s):
    stack = []
    number = 0
    op = "+"                         # the operator BEFORE the current number
    for ch in s + "+":               # a final "+" flushes the last number
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch == " ":
            continue
        else:
            if op == "+":
                stack.append(number)
            elif op == "-":
                stack.append(-number)
            elif op == "*":
                stack.append(stack.pop() * number)
            else:
                stack.append(trunc_div(stack.pop(), number))
            op = ch
            number = 0
    return sum(stack)

for s in ["3+2*2", " 3/2 ", " 3+5 / 2 ", "14-3/2", "2*3*4", "7-8/2*3"]:
    print(repr(s), calculate2(s))
```
```text
'3+2*2' 7
' 3/2 ' 1
' 3+5 / 2 ' 5
'14-3/2' 13
'2*3*4' 24
'7-8/2*3' -5
```

Notice that we apply the operator that came **before** the number we just finished reading; that is why `op` starts as `"+"` and the extra `"+"` at the end is needed. Check `7-8/2*3`: the terms are `7`, then `-8` becomes `-4` after `/2`, then `-12` after `*3`. Sum: `7 - 12 = -5`.

**Try it 3.** Use `to_postfix` and `eval_rpn` to evaluate `"2 * (3 + 4) - 5"`. What are the postfix tokens?

<details><summary>Answer</summary>

```python
import re

PREC = {"+": 1, "-": 1, "*": 2, "/": 2}

def to_postfix(tokens):
    out, ops = [], []
    for t in tokens:
        if t.isdigit():
            out.append(t)
        elif t in PREC:
            while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[t]:
                out.append(ops.pop())
            ops.append(t)
        elif t == "(":
            ops.append(t)
        else:
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()
    while ops:
        out.append(ops.pop())
    return out

def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b = stack.pop(); a = stack.pop()
            stack.append({"+": a + b, "-": a - b, "*": a * b, "/": a // b}[t])
        else:
            stack.append(int(t))
    return stack[0]

postfix = to_postfix(re.findall(r"\d+|[-+*/()]", "2 * (3 + 4) - 5"))
print(postfix)
print(eval_rpn(postfix))
```
```text
['2', '3', '4', '+', '*', '5', '-']
9
```

Postfix: `2 3 4 + * 5 -`. The brackets force `3 + 4` to be done first (7), then `2 * 7 = 14`, then `14 - 5 = 9`.

</details>

### What these programs do not handle

All the programs above assume the input is correct and uses only non-negative integers. A real calculator also needs unary minus (`-3 + 2`, `2 * -3`), decimals, and error messages. Unary minus is the usual trap: a `-` that follows an operator or `(` (or starts the text) means "negate", not "subtract". If a problem asks for it, treat that `-` as a special token or insert a `0` before it.

## 7. Stack tricks for strings

Whenever you process a string and the rule is "look at the latest thing, and maybe undo it", think stack. Four short problems, one idea each.

### Simplify a file path

`/home//foo/../bar/./baz/` should become `/home/bar/baz`. Split by `/`. An empty part or a `.` changes nothing. A `..` goes **up one folder**: pop the last folder if there is one. Anything else is a folder name: push it.

```python
def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)

for p in ["/home/", "/../", "/home//foo/", "/a/./b/../../c/", "/a/../../b/../c//.//"]:
    print(f"{p:24} -> {simplify_path(p)}")
```
```text
/home/                   -> /home
/../                     -> /
/home//foo/              -> /home/foo
/a/./b/../../c/          -> /c
/a/../../b/../c//.//     -> /c
```

Going up from the root (`/..`) stays at the root, which is why `..` with an empty stack does nothing.

### Decode a nested string

`3[a2[c]]` means "3 times (`a` followed by 2 times `c`)", so the answer is `accaccacc`. The inner part must be finished before the outer part. When you read `[`, you suspend the current string and the number before it. When you read `]`, you repeat the finished piece and glue it onto the suspended string.

```python
def decode(s):
    stack = []                     # holds (string before "[", repeat count)
    current = ""
    k = 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)           # numbers may have several digits: 12[x]
        elif ch == "[":
            stack.append((current, k))
            current, k = "", 0
        elif ch == "]":
            before, count = stack.pop()
            current = before + current * count
        else:
            current += ch
    return current

for s in ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef", "10[z]", "a"]:
    print(repr(s), "->", repr(decode(s)))
```
```text
'3[a]2[bc]' -> 'aaabcbc'
'3[a2[c]]' -> 'accaccacc'
'2[abc]3[cd]ef' -> 'abcabccdcdcdef'
'10[z]' -> 'zzzzzzzzzz'
'a' -> 'a'
```

### Remove adjacent duplicates

Repeatedly delete two equal neighbouring letters: `abbaca` -> `aaca` -> `ca`. A stack does it in one pass: if the new letter equals the top, **pop** (they cancel); otherwise push.

```python
def remove_duplicates(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)

print(remove_duplicates("abbaca"), remove_duplicates("azxxzy"), repr(remove_duplicates("aabb")))
```
```text
ca ay ''
```

A harder form: delete `k` equal neighbours at once. Store `[letter, count]` on the stack; increase the count when the letter repeats; pop when the count reaches `k`.

```python
def remove_k_duplicates(s, k):
    stack = []                          # each entry: [letter, run length]
    for ch in s:
        if stack and stack[-1][0] == ch:
            stack[-1][1] += 1
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append([ch, 1])
    return "".join(letter * count for letter, count in stack)

print(remove_k_duplicates("deeedbbcccbdaa", 3))
print(remove_k_duplicates("pbbcggttciiippooaais", 2))
```
```text
aa
ps
```

### Compare strings with backspaces

In `"ab#c"`, the `#` is a backspace that deletes the `b`, so the text is `ac`. A stack is a text buffer where a backspace is a pop.

```python
def type_text(s):
    buffer = []
    for ch in s:
        if ch == "#":
            if buffer:
                buffer.pop()
        else:
            buffer.append(ch)
    return "".join(buffer)

def backspace_equal(a, b):
    return type_text(a) == type_text(b)

print(type_text("ab#c"), type_text("a##c"), repr(type_text("#a#")))
print(backspace_equal("ab#c", "ad#c"), backspace_equal("a#c", "b"))
```
```text
ac c ''
True False
```

This uses `O(n)` extra space. There is a clever `O(1)`-space version that walks both strings from the **end** with two pointers, counting pending backspaces. It is a good exercise after the stack version works.

**Predict the output 4.** What does `decode` give for `"2[a]b"`, and for `"2[2[a]b]"`?

<details><summary>Answer</summary>

```python
def decode(s):
    stack = []
    current = ""
    k = 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)
        elif ch == "[":
            stack.append((current, k))
            current, k = "", 0
        elif ch == "]":
            before, count = stack.pop()
            current = before + current * count
        else:
            current += ch
    return current

print(decode("2[a]b"))
print(decode("2[2[a]b]"))
```
```text
aab
aabaab
```

`2[a]b` is `aa` followed by `b`. In `2[2[a]b]`, the inner `2[a]` is `aa`, then `b` follows: the unit is `aab`, and it repeats twice: `aabaab`. The letter after a `]` belongs to the enclosing level.

</details>

## 8. Designing with stacks and queues

Interviewers like this kind of question: "build a data structure with these operations in these times". They test whether you understand the structures well enough to combine them.

### A stack that knows its minimum

Support `push`, `pop`, `top` and `get_min`, all in `O(1)`. Finding the minimum by scanning would cost `O(n)`. The idea: with every element, remember **the minimum of the stack at that moment**. When an element is popped, the minimum of what is left is already written on the new top.

```python
class MinStack:
    def __init__(self):
        self.items = []                    # each entry: (value, minimum up to here)

    def push(self, x):
        current_min = min(x, self.items[-1][1]) if self.items else x
        self.items.append((x, current_min))

    def pop(self):
        return self.items.pop()[0]

    def top(self):
        return self.items[-1][0]

    def get_min(self):
        return self.items[-1][1]

m = MinStack()
for x in (5, 3, 7, 3, 8):
    m.push(x)
    print("push", x, "min =", m.get_min())
for _ in range(3):
    print("pop", m.pop(), "min =", m.get_min())
```
```text
push 5 min = 5
push 3 min = 3
push 7 min = 3
push 3 min = 3
push 8 min = 3
pop 8 min = 3
pop 3 min = 3
pop 7 min = 3
```

Trace it: after popping `8`, `3` and `7`, the stack is `[5, 3]` and the minimum is `3`, with no scan. The price is extra memory: one more number per element. The same trick gives a "max stack".

### A queue from two stacks

A stack reverses order; reversing twice gives the original order. Use an **inbox** stack for new items and an **outbox** stack for removal. To dequeue: if the outbox is empty, move *everything* from the inbox to the outbox (this reverses it, so the oldest is on top); then pop the outbox.

```python
class QueueFromStacks:
    def __init__(self):
        self.inbox = []
        self.outbox = []
        self.moves = 0                     # counts how often we move an item

    def push(self, x):
        self.inbox.append(x)

    def _refill(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())
                self.moves += 1

    def pop(self):
        self._refill()
        return self.outbox.pop()

    def peek(self):
        self._refill()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox

q = QueueFromStacks()
for x in (1, 2, 3):
    q.push(x)
print(q.pop())
q.push(4)
print(q.pop(), q.pop(), q.pop())
print("moves:", q.moves, "for 4 items")
```
```text
1
2 3 4
moves: 4 for 4 items
```

One `pop` can be slow (it may move many items), but each item moves from the inbox to the outbox **at most once** in its life. So `n` pushes and `n` pops cost `O(n)` in total, which is `O(1)` **amortised** per operation. This is a standard argument; learn the sentence: "every element is moved at most once, so the total work is linear."

### A stack from a queue

The other direction: use one queue so that the *newest* item comes out first. After each push, rotate the queue so that the new item moves to the front. `push` is `O(n)` and `pop` is `O(1)`.

```python
from collections import deque

class StackFromQueue:
    def __init__(self):
        self.q = deque()

    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):       # move all older items behind x
            self.q.append(self.q.popleft())

    def pop(self):
        return self.q.popleft()

    def top(self):
        return self.q[0]

s = StackFromQueue()
for x in (1, 2, 3):
    s.push(x)
print(s.pop(), s.pop(), s.top())
```
```text
3 2 1
```

### Undo and redo

An editor needs two stacks: the **undo** stack holds earlier states, the **redo** stack holds states that were undone. A new edit clears the redo stack, because the "future" you undid no longer exists.

```python
class Editor:
    def __init__(self):
        self.text = ""
        self.undo_stack = []
        self.redo_stack = []

    def type(self, s):
        self.undo_stack.append(self.text)
        self.text += s
        self.redo_stack.clear()                # a new edit kills the redo history

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.text)
            self.text = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.text)
            self.text = self.redo_stack.pop()

e = Editor()
e.type("ab"); e.type("cd")
print(repr(e.text))
e.undo(); print(repr(e.text))
e.undo(); print(repr(e.text))
e.redo(); print(repr(e.text))
e.type("X"); print(repr(e.text))
e.redo(); print(repr(e.text))
```
```text
'abcd'
'ab'
''
'ab'
'abX'
'abX'
```

The browser's **back** and **forward** buttons work the same way: two stacks, and visiting a new page clears the forward stack.

**Try it 4.** In `QueueFromStacks`, what goes wrong if `pop` moves items from the inbox to the outbox *even when the outbox is not empty*? Test it by hand with pushes `1, 2`, a pop, a push `3`, and two pops.

<details><summary>Answer</summary>

```python
class BrokenQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def pop(self):
        while self.inbox:                      # BUG: no "if not self.outbox" check
            self.outbox.append(self.inbox.pop())
        return self.outbox.pop()

q = BrokenQueue()
q.push(1); q.push(2)
first = q.pop()
q.push(3)
print(first, q.pop(), q.pop())
```
```text
1 3 2
```

The correct order is `1, 2, 3`. After the first pop, the outbox holds `[2]`. The broken version then moves `3` on top of it, so the outbox is `[2, 3]` and the next pop returns `3` before `2`: the queue order is destroyed. The rule is: **refill the outbox only when it is empty**, because the items already in it are older than anything in the inbox.

</details>

## 9. The monotonic stack: next greater element

This is the most important idea of the module. A whole family of problems ("for each item, find the next bigger one", "how long until it gets warmer", "how far back was something smaller") look like they need two nested loops. A stack with one extra rule solves them in `O(n)`.

### The problem

For each number in a list, find the **next greater element**: the first number to its right that is strictly larger. If there is none, the answer is `-1`.

`[2, 1, 2, 4, 3]` -> `[4, 2, 4, -1, -1]`. The first `2` is followed by `1`, `2`, then `4`: the first larger one is `4`. The `1` sees `2` next. The last two numbers have nothing bigger to their right.

### The slow way

For each position, scan to the right until you meet something larger. That is two nested loops, `O(n^2)`, and `n = 10^5` is too much.

```python
def next_greater_slow(nums):
    n = len(nums)
    ans = [-1] * n
    for i in range(n):
        for j in range(i + 1, n):
            if nums[j] > nums[i]:
                ans[i] = nums[j]
                break
    return ans

print(next_greater_slow([2, 1, 2, 4, 3]))
```
```text
[4, 2, 4, -1, -1]
```

### The idea: a waiting room

Scan once from left to right. Think of each element as a person **waiting for someone taller to arrive**. Keep the waiting people in a stack. When a new number `x` arrives:

- Everyone in the waiting room who is **smaller than `x`** has found their answer: it is `x`. Remove them (pop).
- Then `x` itself goes into the waiting room (push), because it has no answer yet.

Why a stack, and why does it work? Look at who is waiting. If `a` is waiting below `b` in the stack, then `a >= b`: otherwise `b` would have resolved `a` when it arrived. So the waiting room is always sorted: the biggest at the bottom, the smallest on top. That is why this is called a **monotonic stack** (monotonic means "only goes one way", here: never increases from bottom to top).
When a new `x` arrives, the people that `x` can resolve are exactly the ones at the **top**, the smallest ones. So we pop from the top while the top is smaller than `x`, and we can stop at the first one that is not.

We store **indices**, not values, because we can get the value from the index, but not the other way round (and later we often need the distance).

```python
def next_greater(nums):
    ans = [-1] * len(nums)
    waiting = []                               # indices whose answer is not known yet
    for i, x in enumerate(nums):
        while waiting and nums[waiting[-1]] < x:
            ans[waiting.pop()] = x             # x is the next greater of the popped one
        waiting.append(i)
    return ans

print(next_greater([2, 1, 2, 4, 3]))
```
```text
[4, 2, 4, -1, -1]
```

### Trace by hand

| i | x | pops (index: gets answer) | waiting (values) after |
|---|---|---|---|
| 0 | 2 | none | `[2]` |
| 1 | 1 | none (2 is not smaller than 1) | `[2, 1]` |
| 2 | 2 | index 1 gets 2 (1 < 2); index 0 stays (2 is not < 2) | `[2, 2]` |
| 3 | 4 | index 2 gets 4; index 0 gets 4 | `[4]` |
| 4 | 3 | none | `[4, 3]` |

At the end, the two people still waiting (4 and 3) have no greater element, so they keep `-1`. Notice that the waiting values are never increasing from bottom to top: `[2]`, `[2,1]`, `[2,2]`, `[4]`, `[4,3]`.

### Why this is `O(n)` and not `O(n^2)`

There is a `while` loop inside a `for` loop, which looks quadratic. But count the **total number of pops**. Each index is pushed exactly once and popped at most once. So the total number of pushes is `n`, the total number of pops is at most `n`, and the whole function does at most `2n` stack operations. The `while` loop sometimes runs a lot and sometimes not at all, but the
*sum* over the whole scan is bounded. This is **amortised** analysis (the same argument as the two-stack queue), and you should be able to say it in one sentence: "each element enters the stack once and leaves once."

### Check against the slow version

A fast algorithm needs a safety net. We test it against the slow, obviously-correct one on many small random lists. (The random generator has a fixed seed, so the test is repeatable.)

```python
import random

rng = random.Random(7)
ok = True
for _ in range(500):
    n = rng.randint(0, 9)
    nums = [rng.randint(0, 5) for _ in range(n)]
    if next_greater(nums) != next_greater_slow(nums):
        ok = False
        print("MISMATCH", nums)
print("500 random lists agree:", ok)
```
```text
500 random lists agree: True
```

Values from 0 to 5 in lists of up to 9 items produce many **equal** neighbours, which is exactly where mistakes with `<` against `<=` show up.

### The same idea, four ways

There are four siblings, and they differ only in two choices: *which direction do I look*, and *how do I compare*.

| Question | Look | Pop while the top is ... | The popped one learns |
|---|---|---|---|
| Next **greater** element | right | smaller than `x` | `x` is its answer |
| Next **smaller** element | right | larger than `x` | `x` is its answer |
| **Previous** greater element | left | smaller than or equal to `x` | after popping, the top is `x`'s answer |
| **Previous** smaller element | left | larger than or equal to `x` | after popping, the top is `x`'s answer |

Two styles hide in this table. In the "next" questions we **answer the popped elements** when the stack pops them. In the "previous" questions we **answer the new element** from whatever is left on top after the pops. Both use the same loop.

```python
def previous_greater(nums):
    ans = [-1] * len(nums)
    stack = []                                     # indices, values decreasing from bottom to top
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] <= x:      # these can never be the answer for later items
            stack.pop()
        if stack:
            ans[i] = nums[stack[-1]]
        stack.append(i)
    return ans

def next_smaller(nums):
    ans = [-1] * len(nums)
    stack = []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] > x:
            ans[stack.pop()] = x
        stack.append(i)
    return ans

nums = [4, 5, 2, 10, 8]
print(previous_greater(nums))
print(next_smaller(nums))
```
```text
[-1, -1, 5, -1, 10]
[2, 2, -1, 8, -1]
```

In `previous_greater`, why can we throw away the popped elements? Take an earlier element `a <= x` on the stack. For any **later** number `y`: if `a > y`, then `x >= a > y` as well, and `x` is closer to `y` than `a` is. So `a` can never be the *closest* greater element for anybody again. That is the logic behind every pop: *an element that can never be useful again is removed*.

### Strictness: what about equal values?

"Next greater" means strictly greater. If you pop with `<=` instead of `<`, you are asking for the next *greater or equal*. The two give different answers when values repeat.

```python
def next_greater_with(nums, or_equal):
    ans = [-1] * len(nums)
    stack = []
    for i, x in enumerate(nums):
        while stack and (nums[stack[-1]] <= x if or_equal else nums[stack[-1]] < x):
            ans[stack.pop()] = x
        stack.append(i)
    return ans

nums = [2, 2, 3]
print("strict         :", next_greater_with(nums, False))
print("greater-or-equal:", next_greater_with(nums, True))
```
```text
strict         : [3, 3, -1]
greater-or-equal: [2, 3, -1]
```

For the first `2`: the strict question skips the second `2` and finds `3`; the "or equal" question stops at the second `2`. Read the problem statement for the exact word. When a task says "span" or "at least as large", it usually wants `<=`.

### Circular arrays

If the list is circular (after the last element comes the first again), the next greater element of the last numbers may be at the start. The trick: go around **twice** (indices `0` to `2n - 1`, using `i % n`), but push only on the first lap.

```python
def next_greater_circular(nums):
    n = len(nums)
    ans = [-1] * n
    stack = []
    for i in range(2 * n):
        x = nums[i % n]
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
        if i < n:
            stack.append(i)
    return ans

print(next_greater_circular([1, 2, 1]))
print(next_greater_circular([1, 2, 3, 4, 3]))
```
```text
[2, -1, 2]
[2, 3, 4, -1, 4]
```

For `[1, 2, 1]` the last `1` wraps around to find `2`. The maximum has no greater element anywhere, so it stays `-1`. We push only on the first lap, so no index is pushed twice and the work stays linear.

### Daily temperatures: distance, not value

Given daily temperatures, for each day find how many days you must wait for a warmer day (0 if never). It is the same problem, but the answer is the **distance** `i - j`. That is why we store indices.

```python
def daily_temperatures(temps):
    ans = [0] * len(temps)
    stack = []                                   # indices of days still waiting for a warmer day
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j                       # days waited
        stack.append(i)
    return ans

print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
```
```text
[1, 1, 4, 2, 1, 1, 0, 0]
```

### Stock span: how far back is it not higher?

For each day, the **span** is the number of consecutive days (ending today, including today) with a price **at most** today's price. This asks for the previous *strictly greater* price, and the answer is the distance to it. We can keep `(price, span)` pairs and **merge** spans when we pop.

```python
class StockSpanner:
    def __init__(self):
        self.stack = []                        # (price, span), prices strictly decreasing

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]        # absorb the days they covered
        self.stack.append((price, span))
        return span

s = StockSpanner()
print([s.next(p) for p in (100, 80, 60, 70, 60, 75, 85)])
```
```text
[1, 1, 1, 2, 1, 4, 6]
```

On the day with price 75, the stack pops 60, 70 and 60 and adds their spans: 1 + 2 + 1, plus 1 for today, gives 4. The pairs let us skip over many days in a single step.

**Predict the output 5.** What does `daily_temperatures([30, 40, 50, 60])` print, and what about `daily_temperatures([60, 50, 40, 30])`?

<details><summary>Answer</summary>

```python
def daily_temperatures(temps):
    ans = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans

print(daily_temperatures([30, 40, 50, 60]))
print(daily_temperatures([60, 50, 40, 30]))
```
```text
[1, 1, 1, 0]
[0, 0, 0, 0]
```

A rising list resolves every waiting day on the very next day, so each answer is 1 (the last has nothing warmer: 0). A falling list resolves nobody: every day is pushed and none is popped, so all answers are 0. These are the two extremes: the stack never holds more than one item, or it holds all `n`.

</details>

**Try it 5.** For each day, find the distance back to the **previous warmer day** (0 if there is none). For `[73, 74, 75, 71, 69, 72, 76, 73]` the answer is `[0, 0, 0, 1, 1, 3, 0, 1]`. Which of the four siblings is this, and what do you store?

<details><summary>Answer</summary>

It is "previous greater", answered at arrival: after the pops, the top of the stack (if any) is the previous warmer day, and the distance is `i - top`. We store indices because we need the distance.

```python
def days_since_warmer(temps):
    ans = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] <= t:
            stack.pop()                     # not warmer than today: never useful again
        if stack:
            ans[i] = i - stack[-1]
        stack.append(i)
    return ans

print(days_since_warmer([73, 74, 75, 71, 69, 72, 76, 73]))
```
```text
[0, 0, 0, 1, 1, 3, 0, 1]
```

Check day 5 (temperature 72): the pops remove 69 and 71, and the top is the day with 75 (index 2), so the distance is `5 - 2 = 3`. Day 6 (76): nothing before it is warmer, so the stack is empty after the pops and the answer is 0. Day 7 (73) has 76 just before it, a distance of 1.

</details>

## 10. More problems for the monotonic stack

The pattern appears in disguise in many problems. The recognition tip: *you need, for each element, the nearest element to its left or right that is bigger or smaller*. Here are the best-known ones.

### Largest rectangle in a histogram

A histogram has bars of width 1 and given heights, for example `[2, 1, 5, 6, 2, 3]`. Find the area of the largest rectangle that fits inside the bars.

The key observation: for a rectangle of the best height, its height is the height of its *shortest bar*. So for each bar `h`, ask: **how far can a rectangle of height `h` be stretched to the left and right?** It stretches until it meets a *smaller* bar on each side. That is "previous smaller" and "next smaller" again.

A single pass with an **increasing stack** (heights never decrease from bottom to top) does both. When a bar arrives that is lower than the top, the top bar has found its right boundary (the new bar) and, below it in the stack, its left boundary (the previous smaller bar, now on top after the pop). The width is the gap between them.

```python
def largest_rectangle(heights):
    stack = []                               # indices, heights increasing
    best = 0
    for i, h in enumerate(heights + [0]):    # the final 0 forces everything to be popped
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1          # the previous smaller bar (or the left edge)
            width = i - left - 1                       # bars strictly between left and i
            best = max(best, height * width)
        stack.append(i)
    return best

for hs in ([2, 1, 5, 6, 2, 3], [2, 4], [5], [], [6, 2, 5, 4, 5, 1, 6]):
    print(hs, largest_rectangle(hs))
```
```text
[2, 1, 5, 6, 2, 3] 10
[2, 4] 4
[5] 5
[] 0
[6, 2, 5, 4, 5, 1, 6] 12
```

Two tricks to remember. First, the **sentinel**: we append a bar of height 0 so that the loop pops everything at the end, with no separate cleanup code. Second, `left = stack[-1] if stack else -1`: if the stack is empty after the pop, the bar is the smallest so far, so its rectangle reaches the left edge.

Trace `[2, 1, 5, 6, 2, 3]`: bars 5 and 6 are pushed after 1. The bar `2` at index 4 pops `6` (height 6, width 1, area 6), then pops `5` (height 5, left is index 1, width 2, area 10). That `10` is the answer: the bars 5 and 6 form a rectangle of height 5 and width 2.

Check it against brute force on random inputs, as always:

```python
import random

def largest_rectangle_slow(heights):
    best = 0
    for i in range(len(heights)):
        low = heights[i]
        for j in range(i, len(heights)):
            low = min(low, heights[j])
            best = max(best, low * (j - i + 1))
    return best

rng = random.Random(11)
ok = all(largest_rectangle(h) == largest_rectangle_slow(h)
         for h in ([rng.randint(0, 6) for _ in range(rng.randint(0, 10))] for _ in range(500)))
print("500 random histograms agree:", ok)
```
```text
500 random histograms agree: True
```

### Maximal rectangle of 1s in a grid

Given a grid of `0` and `1`, find the largest rectangle of only `1`s. Build a histogram row by row: `height[c]` is the number of consecutive `1`s ending at the current row in column `c`. Each row is then a histogram problem.

```python
def maximal_rectangle(grid):
    if not grid:
        return 0
    heights = [0] * len(grid[0])
    best = 0
    for row in grid:
        for c, cell in enumerate(row):
            heights[c] = heights[c] + 1 if cell == "1" else 0
        best = max(best, largest_rectangle(heights))
    return best

grid = [list("10100"),
        list("10111"),
        list("11111"),
        list("10010")]
print(maximal_rectangle(grid))
```
```text
6
```

The cost is `O(rows x cols)`: each row costs one linear pass. The grid problem turned into the histogram problem by a change of view, which is a typical way to solve "hard" problems.

### Trapping rain water

Bars of given heights stand side by side. After rain, how much water stays between them? Water above a bar is held between the nearest higher walls on its left and right: `min(left wall, right wall) - bar height`.

A **decreasing stack** finds it level by level. When a bar arrives that is higher than the top, the top is the *bottom of a pool*. The bar below it in the stack is the left wall and the new bar is the right wall. The pool's width is the gap between the walls, and its depth is `min(left, right) - bottom`.

```python
def trap(height):
    stack = []                                # indices, heights decreasing
    water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break                         # no left wall: the water would run away
            left = stack[-1]
            width = i - left - 1
            depth = min(height[left], h) - height[bottom]
            water += width * depth
        stack.append(i)
    return water

print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))
print(trap([4, 2, 0, 3, 2, 5]))
print(trap([]), trap([3]), trap([3, 3]))
```
```text
6
9
0 0 0
```

Each pop adds one horizontal "layer" of water. There is also a two-pointer solution with `O(1)` extra space (you saw the pointers technique in dsa.03). The stack version is the one to learn because it generalises to "2D" histograms.

### Sum of subarray minimums: the contribution technique

Given an array, find the sum of `min(subarray)` over **all** subarrays. There are `n(n+1)/2` subarrays, so listing them is `O(n^2)` or worse. Turn the question around: for each element, **in how many subarrays is it the minimum?** An element `arr[i]` is the minimum of a subarray if the subarray stays between the previous smaller element (on the left) and the next smaller element (on the right). If the previous smaller is at `p` and the next smaller at `q`, the subarray may start in `i - p` places and end in `q - i` places, which gives `(i - p) * (q - i)` subarrays.

Total = the sum over `i` of `arr[i] * (i - p) * (q - i)`. We find `p` and `q` for all `i` with the monotonic stack.

**Careful with equal values.** If two equal numbers can both be "the minimum", a subarray with both would be counted twice. Make the rule asymmetric: on the left, the previous *strictly smaller* element; on the right, the next *smaller or equal* element. Then each subarray is credited to exactly one position (its rightmost minimum).

```python
def sum_subarray_mins(arr):
    n = len(arr)
    prev = [-1] * n                    # nearest index on the left with a strictly smaller value
    stack = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        prev[i] = stack[-1] if stack else -1
        stack.append(i)

    nxt = [n] * n                      # nearest index on the right with a smaller-or-equal value
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        nxt[i] = stack[-1] if stack else n
        stack.append(i)

    return sum(arr[i] * (i - prev[i]) * (nxt[i] - i) for i in range(n))

def sum_subarray_mins_slow(arr):
    return sum(min(arr[i:j + 1]) for i in range(len(arr)) for j in range(i, len(arr)))

print(sum_subarray_mins([3, 1, 2, 4]), sum_subarray_mins([11, 81, 94, 43, 3]))

import random
rng = random.Random(3)
ok = all(sum_subarray_mins(a) == sum_subarray_mins_slow(a)
         for a in ([rng.randint(1, 4) for _ in range(rng.randint(0, 9))] for _ in range(500)))
print("500 random lists agree:", ok)
```
```text
17 444
500 random lists agree: True
```

The random test uses only the values 1 to 4, so there are many equal numbers: that is where a symmetric (wrong) tie rule would give a mismatch. This "count the contribution of each element" idea also solves "sum of subarray maximums", and "number of subarrays where `x` is the maximum".

### Remove k digits to make the smallest number

Given a digit string `num` and `k`, remove exactly `k` digits so the remaining number is as small as possible. Greedy view: scanning from left, if a digit is **larger than the one after it**, removing it makes the number smaller (a smaller digit moves into a more important position). So keep the stack **increasing**; when a new digit is smaller than the top, pop the top (that is a removal) while removals are left.

```python
def remove_k_digits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    if k:                                       # still removals left: the stack is increasing, drop the largest (the end)
        stack = stack[:-k]
    return "".join(stack).lstrip("0") or "0"

for num, k in (("1432219", 3), ("10200", 1), ("10", 2), ("9", 1), ("112", 1)):
    print(num, k, "->", remove_k_digits(num, k))
```
```text
1432219 3 -> 1219
10200 1 -> 200
10 2 -> 0
9 1 -> 0
112 1 -> 11
```

Three edge cases are all in the code: leftover removals (`"112"`, `k = 1`: the digits only increase, so remove from the end), leading zeros (`"10200"` gives `"200"`), and an empty result (which must be printed as `"0"`). Test all three whenever you write this.

**Try it 6.** What does `largest_rectangle([3, 3, 3])` return, and why does it work even though no bar is ever strictly smaller than the top? (Hint: the condition uses `>=`.)

<details><summary>Answer</summary>

```python
def largest_rectangle(heights):
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            width = i - left - 1
            best = max(best, height * width)
        stack.append(i)
    return best

print(largest_rectangle([3, 3, 3]))
```
```text
9
```

The answer is 9 (height 3, width 3). The sentinel 0 at the end pops all three bars. The last popped bar sees an empty stack (left = -1) and gets the width `3 - (-1) - 1 = 3`. With `>=`, equal bars are popped by their equal neighbour, so the earlier ones compute a small rectangle that is not wrong (just not the best), and the last equal bar computes the full width. Both `>` and `>=` give the correct final answer; `>=` keeps the stack strictly increasing.

</details>

## 11. The monotonic queue: sliding window maximum

A stack removes unneeded items from **one** end. A **monotonic queue** (a deque) removes unneeded items from the *back* and also expires old items from the *front*. Its classic use is the maximum (or minimum) of every window of size `k`.

### The problem

For `[1, 3, -1, -3, 5, 3, 6, 7]` and `k = 3`, the windows are `[1,3,-1]`, `[3,-1,-3]`, `[-1,-3,5]`, `[-3,5,3]`, `[5,3,6]`, `[3,6,7]`, with maxima `[3, 3, 5, 5, 6, 7]`.

The slow way finds the maximum of each window with `max(window)`: `O(n * k)`. A heap gives `O(n log n)`. The deque gives `O(n)`.

### The idea

Keep a deque of **indices** whose values are in **decreasing** order (front = largest). The front is always the maximum of the current window.

When index `i` arrives:

1. **Back:** while the value at the back is **smaller than or equal to** `nums[i]`, remove it. It is older *and* smaller, so it can never be the maximum of any window that also contains `i`. (This is the same "useless forever" argument as in the stack.)
2. **Add** `i` at the back.
3. **Front:** if the index at the front is `<= i - k`, it has left the window: remove it.
4. When `i >= k - 1` (the first window is complete), the front is the answer for this window.

```python
from collections import deque

def sliding_window_max(nums, k):
    dq = deque()                       # indices, values decreasing from front to back
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                   # smaller and older than x: useless from now on
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()               # the front index has left the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
```
```text
[3, 3, 5, 5, 6, 7]
```

### Trace of the deque (values shown, indices in brackets)

| i | x | deque after (index:value) | window max |
|---|---|---|---|
| 0 | 1 | `0:1` | |
| 1 | 3 | pop `0:1` (1 <= 3); push -> `1:3` | |
| 2 | -1 | `1:3, 2:-1` | 3 |
| 3 | -3 | `1:3, 2:-1, 3:-3` | 3 |
| 4 | 5 | pop all three (all <= 5); push -> `4:5` | 5 |
| 5 | 3 | `4:5, 5:3` | 5 |
| 6 | 6 | pop `5:3`, pop `4:5`; push -> `6:6` | 6 |
| 7 | 7 | pop `6:6`; push -> `7:7` | 7 |

In this example the front never expires by itself, because larger values keep arriving and push the old ones out from the back. The front check matters when a large value sits at the front and **no larger value arrives**. Try `[9, 3, 2, 1]` with `k = 2`:

```python
print(sliding_window_max([9, 3, 2, 1], 2))
```
```text
[9, 3, 2]
```

At `i = 2` the deque holds the indices `0, 1, 2`. The front index `0` satisfies `0 <= 2 - 2`, so the `9` has left the window and is removed. The window `[3, 2]` has maximum `3`. Without the front check, the program would wrongly say `9` for this window.

Total work: every index is added once and removed at most once (from the back or the front), so the whole scan is `O(n)`.

```python
import random

def window_max_slow(nums, k):
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]

rng = random.Random(5)
ok = True
for _ in range(500):
    n = rng.randint(1, 12)
    nums = [rng.randint(-3, 3) for _ in range(n)]
    k = rng.randint(1, n)
    if sliding_window_max(nums, k) != window_max_slow(nums, k):
        ok = False
        print("MISMATCH", nums, k)
print("500 random cases agree:", ok)
```
```text
500 random cases agree: True
```

For the **minimum** of each window, flip the comparison: pop from the back while `nums[dq[-1]] >= x`. The deque is then increasing and the front is the minimum.

### Two deques: the longest window with a small range

Find the longest subarray in which `max - min <= limit`. Keep a **max-deque** and a **min-deque** of the current window. Move the right end one step at a time; when the range is too big, shrink from the left until it is fine. Remove the left element from a deque only if it is the one at the deque's front.

```python
from collections import deque

def longest_subarray(nums, limit):
    maxd, mind = deque(), deque()          # values (not indices): decreasing, increasing
    left = 0
    best = 0
    for right, x in enumerate(nums):
        while maxd and maxd[-1] < x:
            maxd.pop()
        maxd.append(x)
        while mind and mind[-1] > x:
            mind.pop()
        mind.append(x)
        while maxd[0] - mind[0] > limit:
            if nums[left] == maxd[0]:
                maxd.popleft()
            if nums[left] == mind[0]:
                mind.popleft()
            left += 1
        best = max(best, right - left + 1)
    return best

print(longest_subarray([8, 2, 4, 7], 4), longest_subarray([10, 1, 2, 4, 7, 2], 5), longest_subarray([4, 2, 2, 2, 4, 4, 2, 2], 0))
```
```text
2 4 3
```

Here the deques store values, not indices. That works because we compare `nums[left]` with the front value: an expiring element leaves the deque only if it is currently the front. With duplicates, `maxd` keeps equal values (we pop only strictly smaller ones), so each copy has its own entry.

### A monotonic queue inside dynamic programming

Many DP recurrences look like `dp[i] = nums[i] + max(dp[i-k], ..., dp[i-1])`: the best of the previous `k` values. Computing the max by a loop costs `O(k)`; a monotonic deque gives it in `O(1)`.

Example: you stand on cell 0 and may jump 1 to `k` steps to the right. Each cell you land on adds its value (it may be negative). What is the maximum total score when you reach the last cell?

```python
from collections import deque

def max_score(nums, k):
    n = len(nums)
    dp = [0] * n
    dp[0] = nums[0]
    dq = deque([0])                         # indices with decreasing dp values
    for i in range(1, n):
        while dq[0] < i - k:
            dq.popleft()                    # too far to jump from
        dp[i] = nums[i] + dp[dq[0]]         # best earlier cell within reach
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return dp[-1]

print(max_score([1, -1, -2, 4, -7, 3], 2))
print(max_score([10, -5, -2, 4, 0, 3], 3))
print(max_score([1, -5, -20, 4, -1, 3, -6, -3], 2))
```
```text
7
17
0
```

You will meet this "DP plus monotonic queue" again in the dynamic programming modules. The recipe is always the same: *a window of earlier states, and I need the best one fast*.

### Shortest subarray with a sum of at least K (with negatives)

With only positive numbers, two pointers solve this. With **negative** numbers they fail (shrinking from the left may make the sum bigger). Use prefix sums and a deque of indices whose prefix sums are **increasing**. For every `i`:

1. While the front index `j` gives `prefix[i] - prefix[j] >= K`, we have a candidate length `i - j`. Pop it: any later `i` would only give a longer subarray with the same `j`.
2. While the back has a prefix sum `>= prefix[i]`, pop it: `i` is later *and* has a smaller-or-equal prefix, so it is always at least as good a starting point.

```python
from collections import deque

def shortest_subarray(nums, K):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)
    dq = deque()
    best = len(nums) + 1
    for i, p in enumerate(prefix):
        while dq and p - prefix[dq[0]] >= K:
            best = min(best, i - dq.popleft())
        while dq and prefix[dq[-1]] >= p:
            dq.pop()
        dq.append(i)
    return best if best <= len(nums) else -1

print(shortest_subarray([1], 1), shortest_subarray([1, 2], 4), shortest_subarray([2, -1, 2], 3))
print(shortest_subarray([84, -37, 32, 40, 95], 167))
```
```text
1 -1 3
3
```

This is one of the hardest problems that use a deque. Its shape is: a window of earlier positions, two reasons to throw positions away (they are *used up* from the front, or *dominated* from the back), and every position enters and leaves once.

**Try it 7.** Change `sliding_window_max` so that it returns the *index* of the maximum of each window instead of its value. Which line changes?

<details><summary>Answer</summary>

Only the line that appends to the output: use `dq[0]` itself, since the deque stores indices.

```python
from collections import deque

def sliding_window_argmax(nums, k):
    dq = deque()
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(dq[0])               # the index, not nums[dq[0]]
    return out

print(sliding_window_argmax([1, 3, -1, -3, 5, 3, 6, 7], 3))
```
```text
[1, 1, 4, 4, 6, 7]
```

Storing indices (not values) in the deque is what makes the expiry test possible. That is why the monotonic structures in this section keep indices unless, as in the two-deque example, comparing values is enough.

</details>

## 12. Queue patterns: simulations and BFS

A queue is the right tool whenever things must be handled **in the order they arrived**, or whenever you explore *level by level*. Here are the main patterns.

### Simulations: hot potato and round robin

**Hot potato (the Josephus problem).** `n` children stand in a circle. Counting from the first child, every `k`-th child leaves the circle. In what order do they leave? Put the children in a deque. To count `k` children, move `k - 1` children from the front to the back (`rotate(-(k-1))`), then the next one at the front leaves.

```python
from collections import deque

def josephus(n, k):
    circle = deque(range(1, n + 1))
    order = []
    while circle:
        circle.rotate(-(k - 1))          # skip k-1 children: they go to the back
        order.append(circle.popleft())   # the k-th child leaves
    return order

print(josephus(7, 3))
print(josephus(5, 2))
```
```text
[3, 6, 2, 7, 5, 1, 4]
[2, 4, 1, 5, 3]
```

The last number in the list is the survivor. A list with `pop(i)` would work too, but each removal from the middle of a list costs `O(n)`, and a rotation of a deque costs `O(k)`.

**Round-robin scheduling.** A computer runs several jobs by giving each a small time slice (the quantum). A job that is not finished goes to the **back of the queue**. This is exactly a queue of "unfinished work".

```python
from collections import deque

def round_robin(jobs, quantum):
    """jobs: list of (name, time needed). Returns {name: time when it finished}."""
    queue = deque(jobs)
    clock = 0
    finished = {}
    while queue:
        name, left = queue.popleft()
        run = min(quantum, left)
        clock += run
        left -= run
        if left:
            queue.append((name, left))       # not done: back of the line
        else:
            finished[name] = clock
    return finished

print(round_robin([("A", 5), ("B", 3), ("C", 1)], 2))
```
```text
{'C': 5, 'B': 8, 'A': 9}
```

Trace it: A runs 2 (clock 2, 3 left, to the back), B runs 2 (clock 4, 1 left), C runs 1 and finishes at 5, A runs 2 (clock 7, 1 left), B runs 1 and finishes at 8, A runs 1 and finishes at 9.

**Generating things in order.** The first `n` binary numbers: `1, 10, 11, 100, 101, ...`. Every number produces two children (add a `0`, add a `1`), and the children must appear after all the numbers shorter than them. A queue does exactly that.

```python
from collections import deque

def first_binary(n):
    queue = deque(["1"])
    out = []
    for _ in range(n):
        s = queue.popleft()
        out.append(s)
        queue.append(s + "0")
        queue.append(s + "1")
    return out

print(first_binary(8))
```
```text
['1', '10', '11', '100', '101', '110', '111', '1000']
```

### Level-order traversal of a tree

In a tree, a node has a value and up to two children. Visiting the nodes **level by level** (the root, then its children, then their children) is a queue: take a node from the front, put its children at the back.

The only new trick is how to know where one level ends. Before processing a level, read `len(queue)`: that is the number of nodes in the level. Process exactly that many.

```python
from collections import deque

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def level_order(root):
    if root is None:
        return []
    queue = deque([root])
    levels = []
    while queue:
        level = []
        for _ in range(len(queue)):          # exactly the nodes of the current level
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels

tree = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
print(level_order(tree))
print(level_order(None))
```
```text
[[3], [9, 20], [15, 7]]
[]
```

`range(len(queue))` is evaluated **once**, when the loop starts, so adding children to the queue inside the loop does not change how many times it runs. That is why this works.

### BFS on a grid: the shortest path

You are in a maze: `.` is free, `#` is a wall. You move up, down, left, right. What is the fewest steps from the start to the goal?

**Why a queue finds the shortest path.** Think of ripples in a pond. All the cells at distance 1 are visited first, then all the cells at distance 2, and so on. A queue keeps this order: cells found earlier are at a smaller distance, and they are processed first. So the first time we reach the goal, we have used the fewest steps. This search is **breadth-first search (BFS)**.

```python
from collections import deque

def shortest_path(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    queue = deque([(start[0], start[1], 0)])       # (row, col, steps so far)
    seen = {start}
    while queue:
        r, c, steps = queue.popleft()
        if (r, c) == goal:
            return steps
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "#" and (nr, nc) not in seen:
                seen.add((nr, nc))                  # mark when we ENQUEUE
                queue.append((nr, nc, steps + 1))
    return -1                                       # the goal cannot be reached

maze = ["..#....",
        ".##.##.",
        "....#..",
        ".##...#",
        "...#..."]
print(shortest_path(maze, (0, 0), (4, 6)))
print(shortest_path(maze, (0, 0), (0, 3)))
print(shortest_path(["..#.", "..#.", "..#."], (0, 0), (0, 3)))
```
```text
10
7
-1
```

The last line is `-1`: a wall splits the grid in two, so the goal cannot be reached. Always decide what to return when there is no path.

### Mark a cell as seen when you enqueue it, not when you dequeue it

This is the most common BFS mistake. If you mark a cell as seen only when you take it out of the queue, then several of its neighbours may put it in the queue **before** it is marked, and it is processed many times. The answer stays correct, but the work grows a lot. Count the number of pushes for an open `n x n` grid:

```python
from collections import deque

def count_pushes(n, mark_when_enqueued):
    queue = deque([(0, 0)])
    seen = {(0, 0)} if mark_when_enqueued else set()
    pushes = 1
    while queue:
        r, c = queue.popleft()
        if not mark_when_enqueued:
            if (r, c) in seen:
                continue
            seen.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen:
                if mark_when_enqueued:
                    seen.add((nr, nc))
                queue.append((nr, nc))
                pushes += 1
    return pushes

print("cells:", 30 * 30)
print("mark when enqueued:", count_pushes(30, True))
print("mark when dequeued:", count_pushes(30, False))
```
```text
cells: 900
mark when enqueued: 900
mark when dequeued: 1741
```

With the right rule, each cell is pushed exactly once. With the wrong rule it is pushed up to four times, and on graphs with high degree the waste is much larger.

### Multi-source BFS: rotting oranges

A grid holds fresh oranges (`1`), rotten oranges (`2`) and empty cells (`0`). Every minute, each fresh orange next to a rotten one becomes rotten. How many minutes until no fresh orange is left? If some can never rot, return `-1`.

All rotten oranges start spreading **at the same time**. So put all of them into the queue at the start (all at distance 0) and run an ordinary BFS, one level per minute.

```python
from collections import deque

def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):               # one minute = one BFS level
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    return minutes if fresh == 0 else -1

print(oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))
print(oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]))
print(oranges_rotting([[0, 2]]))
```
```text
4
-1
0
```

The second grid has a fresh orange in the bottom-left corner, isolated by empty cells: it can never rot, so `-1`. The third has no fresh orange at all: 0 minutes. The "multi-source" idea (start the queue with many sources at once) is used for "distance to the nearest 0", "nearest exit", and many similar problems.

### 0-1 BFS: when some steps are free

What if moving into some cells costs 0 and into others costs 1 (for example, removing an obstacle)? Ordinary BFS assumes every step costs the same. A **0-1 BFS** uses a deque: a free step goes to the **front** (it is at the same distance, so it should be processed next), and a costly step goes to the back.

```python
from collections import deque

def min_obstacles(grid):
    """grid[r][c] is 1 for an obstacle (costs 1 to remove) and 0 for a free cell."""
    rows, cols = len(grid), len(grid[0])
    INF = float("inf")
    dist = [[INF] * cols for _ in range(rows)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                nd = dist[r][c] + grid[nr][nc]
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    if grid[nr][nc] == 0:
                        dq.appendleft((nr, nc))      # a free step: handle it at once
                    else:
                        dq.append((nr, nc))
    return dist[-1][-1]

print(min_obstacles([[0, 1, 1], [1, 1, 0], [1, 1, 0]]))
print(min_obstacles([[0, 1, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 1, 0]]))
```
```text
2
0
```

The deque keeps the distances in sorted order (all the nodes at distance `d`, then `d + 1`), which is the property a queue gave to the plain BFS. It is an `O(cells)` algorithm, where Dijkstra's algorithm with a heap would cost `O(cells log cells)`.

### The same loop with a stack: DFS

Take the BFS loop and replace `popleft()` by `pop()`: the next item to process is the **newest**, not the oldest. The search now goes deep along one path before it comes back. That is **depth-first search (DFS)**, the explicit-stack form of the recursion from dsa.07.

```python
from collections import deque

graph = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": ["F"], "F": []}

def traverse(start, use_stack):
    todo = deque([start])
    seen = {start}
    order = []
    while todo:
        node = todo.pop() if use_stack else todo.popleft()
        order.append(node)
        neighbours = graph[node]
        for nxt in (reversed(neighbours) if use_stack else neighbours):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return order

print("queue (BFS):", traverse("A", False))
print("stack (DFS):", traverse("A", True))
```
```text
queue (BFS): ['A', 'B', 'C', 'D', 'E', 'F']
stack (DFS): ['A', 'B', 'D', 'E', 'F', 'C']
```

BFS visits `A`, then both neighbours `B`, `C`, then their neighbours. DFS goes `A`, `B`, `D` (as deep as possible), comes back to `E`, then `F`, and only then `C`. (For the stack we push the neighbours in reverse order, so that the first neighbour is popped first.) One line decides the whole behaviour: *stack = depth first, queue = breadth first*. Later modules build the full graph theory on this.

**Predict the output 6.** `josephus(5, 2)`: who leaves first, who is the survivor?

<details><summary>Answer</summary>

```python
from collections import deque

def josephus(n, k):
    circle = deque(range(1, n + 1))
    order = []
    while circle:
        circle.rotate(-(k - 1))
        order.append(circle.popleft())
    return order

print(josephus(5, 2))
```
```text
[2, 4, 1, 5, 3]
```

With `k = 2`, every second child leaves: child 2, then 4, then 1 (counting continues around the circle), then 5. Child 3 is the last one left: the survivor.

</details>

**Try it 8.** In `level_order`, how would you change the code to return the levels in **zigzag** order (left to right on level 0, right to left on level 1, and so on)? (Hint: you do not need a second queue.)

<details><summary>Answer</summary>

Keep the BFS as it is. After collecting each level, reverse it on every odd level.

```python
from collections import deque

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def zigzag(root):
    if root is None:
        return []
    queue = deque([root])
    levels = []
    left_to_right = True
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level if left_to_right else level[::-1])
        left_to_right = not left_to_right
    return levels

tree = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, None, TreeNode(6)))
print(zigzag(tree))
```
```text
[[1], [3, 2], [4, 5, 6]]
```

The queue is still filled left to right; only the stored list is reversed. Trying to fill the queue in a different order would break the BFS levels.

</details>

## 13. When a plain queue is not enough: a first look at the heap

A queue gives the **oldest** item. Sometimes you want the **most important** one: the cheapest edge, the task with the highest priority, the smallest number. That is a **priority queue**, and in Python it is a **heap** (the `heapq` module). You will learn how a heap works inside in a later module; here you only need the interface and the cost.

```python
import heapq

heap = []
heapq.heappush(heap, (3, "write report"))
heapq.heappush(heap, (1, "fix bug"))
heapq.heappush(heap, (2, "reply to mail"))
while heap:
    priority, task = heapq.heappop(heap)
    print(priority, task)

print(heapq.nlargest(3, [5, 1, 9, 3, 7, 8]))
print(heapq.nsmallest(2, [5, 1, 9, 3, 7, 8]))
```
```text
1 fix bug
2 reply to mail
3 write report
[9, 8, 7]
[1, 3]
```

| Operation | Queue (`deque`) | Heap (`heapq`) |
|---|---|---|
| add | `append`, `O(1)` | `heappush`, `O(log n)` |
| take the next one | `popleft` (the oldest), `O(1)` | `heappop` (the smallest), `O(log n)` |
| look at the next one | `d[0]`, `O(1)` | `heap[0]`, `O(1)` |

The heap pays `O(log n)` for the privilege of choosing by priority. If all priorities are equal (or equal to "arrival time"), a queue is enough and faster. Use a heap when "the next item" depends on a value, not on the arrival order.

A word of warning about **ties**. `heapq` compares the tuples element by element. If two items have the same priority, Python compares the second element, which fails if it is something that cannot be compared (for example, two dictionaries). The usual fix is to put an increasing counter in the middle: `(priority, counter, item)`.

## 14. Which structure for which problem?

| Clue in the problem | Structure |
|---|---|
| "most recent first", "undo", "nested", "matching pairs" | stack (list) |
| Brackets, tags, expressions, decoding, paths with `..` | stack |
| "for each element, the next greater or smaller" | monotonic stack |
| "previous greater or smaller", "how far back", "span" | monotonic stack |
| "largest rectangle", "trapped water" (bars and walls) | monotonic stack |
| "in order of arrival", "first come first served", simulation of lines | queue (`deque`) |
| "shortest number of steps" when every step costs the same | BFS with a queue |
| "all sources spread at the same time" | multi-source BFS |
| steps cost 0 or 1 | 0-1 BFS with a deque (`appendleft`) |
| "maximum (or minimum) of every window of size k" | monotonic deque |
| "last k items", a moving window | `deque(maxlen=k)` |
| "the best of the previous k states" in DP | monotonic deque |
| "the smallest (or the most urgent) next" | heap |
| need a minimum, maximum or sum inside a design question | stack of pairs, or two stacks |

When two choices seem possible, ask these questions in order:

1. **Which element do I need to take next?** The newest -> stack. The oldest -> queue. The best by value -> heap.
2. **Do I only need the nearest bigger or smaller neighbour?** -> monotonic stack.
3. **Do I need a window statistic?** -> monotonic deque.
4. **Do I need to remove from both ends?** -> deque.

## 15. Costs, and how Python behaves

### The costs in one place

| Structure and operation | Cost |
|---|---|
| `list.append`, `list.pop()` (right end) | `O(1)` (amortised for `append`) |
| `list.pop(0)`, `list.insert(0, x)` | `O(n)`: avoid for queues |
| `deque.append`, `appendleft`, `pop`, `popleft` | `O(1)` |
| `deque[i]` in the middle | `O(n)` |
| `x in list`, `x in deque` | `O(n)` |
| `x in set` | `O(1)` average |
| `len(...)` | `O(1)` |
| `deque.rotate(k)` | `O(k)` |
| monotonic stack over `n` items | `O(n)` in total (each item pushed and popped once) |
| monotonic deque over `n` items | `O(n)` in total |
| BFS on a grid with `V` cells | `O(V)` time, `O(V)` space |

### The amortised argument, once more

Several algorithms in this module have a `while` loop inside a `for` loop and still run in `O(n)`. The reasoning is always the same, and you should be able to write it in two sentences:

1. Each element is **pushed once** (so there are at most `n` pushes).
2. Each element is **popped at most once** (so there are at most `n` pops, over the *whole* run, not per iteration).

Hence the total work of all the inner loops together is at most `2n`. This works for the monotonic stack, the monotonic queue, the queue made of two stacks, and BFS.

```python
def next_greater_counted(nums):
    ans = [-1] * len(nums)
    stack = []
    pushes = pops = 0
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
            pops += 1
        stack.append(i)
        pushes += 1
    return pushes, pops

import random
rng = random.Random(1)
for n in (10, 1000, 100000):
    nums = [rng.randint(0, 10**6) for _ in range(n)]
    pushes, pops = next_greater_counted(nums)
    print(f"n={n:>6}: pushes={pushes:>6}  pops={pops:>6}  total <= 2n: {pushes + pops <= 2 * n}")
```
```text
n=    10: pushes=    10  pops=     6  total <= 2n: True
n=  1000: pushes=  1000  pops=   988  total <= 2n: True
n=100000: pushes=100000  pops= 99985  total <= 2n: True
```

### Memory

The stack of a monotonic algorithm can hold up to `n` indices (a list that only decreases never pops). BFS stores a "frontier": on a big open grid, the frontier is as wide as the ripple. Both are `O(n)` in the worst case, so for `n` around 10^6 it is wise to store integers (indices) and not big objects.

### From recursion to a stack

A recursive function that goes deep (like DFS on a path of 10^5 nodes) hits Python's recursion limit. The fix is an explicit stack (section 15 of dsa.07 and the traversal above). The pattern is: put the starting state on the stack; while the stack is not empty, pop a state, process it, and push the states that come next. Everything you learn about stacks here is what stands behind that.

## 16. Common traps, collected

1. **Popping from an empty stack or queue.** Guard with `if stack:` / `while stack and ...`. In `while stack and nums[stack[-1]] < x`, the `stack and` part must come first.
2. **`list.pop(0)` as a queue.** It works, but costs `O(n)` per removal. Use `deque.popleft()`.
3. **Storing values when you need indices** (or the other way round). If the answer is a distance, or if the item must expire from a window, store the index.
4. **Strict against non-strict comparison** in a monotonic stack. `<` and `<=` give different answers when values repeat. Read the problem for the exact words ("greater", "greater or equal", "at least", "at most").
5. **Forgetting the leftovers.** After the scan, the stack may still hold items (unmatched openers, elements with no greater element). Decide what they mean: return `False`, keep `-1`, or add them to the result.
6. **Wrong operand order for `-` and `/`** in postfix evaluation: the first pop is the right operand.
7. **Division that rounds the wrong way.** `-7 // 2` is `-4` in Python; many problems want `-3`. Use a truncating division helper.
8. **Marking visited too late in BFS.** Mark a cell when you enqueue it.
9. **Refilling the outbox while it still has items** in a queue made of two stacks, which breaks the order.
10. **Using `deque[i]` in a loop** over a big deque, which costs `O(n)` per access and makes the loop quadratic.
11. **Forgetting the sentinel** (the `0` bar in the histogram, the `-1` in the longest valid parentheses, the extra `"+"` in the calculator). The sentinel replaces special cases.
12. **Equal values in the contribution technique.** Count each subarray once: use `<` on one side and `<=` on the other.
13. **Changing the container while looping over it.** Do not `append` to a list you iterate with `for x in lst`. Use `while queue:` and `popleft()` instead.
14. **Level-order loops that read `len(queue)` in the `for` condition after pushing.** Write `for _ in range(len(queue))` (evaluated once) and not `while` with a changing length.

## 17. Summary

- A **stack** is last in, first out: the right end of a Python `list` (`append`, `pop()`, `s[-1]`), all `O(1)`. A **queue** is first in, first out: `collections.deque` (`append`, `popleft()`). `list.pop(0)` is `O(n)`: never use it as a queue.
- Use a stack for **"the most recent unfinished thing"**: brackets, nested strings, paths, expression evaluation, undo, and the call stack of recursion.
- **Balanced brackets**: push openers, pop for each closer, check that the pair matches and that the stack is empty at the end. Three ways to fail: wrong closer, closer on an empty stack, leftover openers.
- **Expressions**: postfix needs only a stack (pop two, push the result; mind the operand order). The shunting-yard method converts infix to postfix with an operator stack. One-pass calculators keep a stack of terms or saved states.
- **Design questions**: a stack of `(value, minimum so far)` gives `O(1)` minimum; two stacks make a queue with `O(1)` amortised operations; a queue can make a stack; two stacks make undo and redo.
- A **monotonic stack** answers "next/previous greater/smaller" for all elements in `O(n)`: pop while the top is worse than the new item, and answer the popped elements (or the new one). Each item is pushed and popped once. Store indices. Be careful with equal values.
- It also solves **daily temperatures, stock span, largest rectangle in a histogram, trapping rain water, sum of subarray minimums, remove k digits**.
- A **monotonic deque** keeps the window maximum (or minimum) at the front: pop worse items from the back, expire old items from the front. It also speeds up DP recurrences over the last `k` states.
- A **queue** drives simulations and **BFS**: level order, shortest path in an unweighted grid, multi-source spreading. Mark visited when you enqueue. With free steps (0-1 BFS) use `appendleft`. Replace `popleft()` by `pop()` and BFS becomes DFS.
- A heap (`heapq`) is the next step when "the next item" is chosen by value, not by arrival.

### Self-check

- [ ] I can implement a stack with a list and a queue with a `deque`, and explain why `pop(0)` is wrong for a queue.
- [ ] I can write the balanced-bracket check and name the three ways it fails.
- [ ] I can evaluate postfix and convert simple infix to postfix.
- [ ] I can build a `MinStack` and a queue from two stacks, and give the amortised argument.
- [ ] I can write next greater, next smaller, previous greater with one monotonic-stack loop, and I know when to use `<` or `<=`.
- [ ] I can compute the largest rectangle in a histogram with the sentinel trick.
- [ ] I can write the sliding-window maximum with a deque of indices.
- [ ] I can write BFS on a grid, mark visited at the right moment, and return `-1` when the goal is unreachable.
- [ ] I can explain why each monotonic algorithm is `O(n)` although it has a `while` inside a `for`.
- [ ] I can choose between stack, queue, deque and heap for a new problem.

### How to practise

Do the problems in the order of the chapter: first plain stack and queue operations, then balanced brackets and string stacks, then expression evaluation, then the design questions, and only then the monotonic ones (they are the hardest idea of the module). For every monotonic-stack problem, write down three things before coding: *what am I waiting for*, *what does an element get when it is popped*, and
*does equality count*. Test each fast solution against a slow, obviously-correct one on small random lists. The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list.

### Further reading

- Robert Sedgewick and Kevin Wayne, *Algorithms*, section 1.3 ("Bags, Queues, and Stacks"), including Dijkstra's two-stack expression evaluation.
- Donald Knuth, *The Art of Computer Programming*, volume 1, section 2.2.1 ("Stacks, Queues, and Deques").
- The Python documentation of `collections.deque` and of the `heapq` module (including the section on priority-queue implementation notes).
- cp-algorithms.com, "Minimum stack / Minimum queue" and "Sparse table" articles, for the ideas behind range-minimum queries.
- The usaco.guide articles "Stacks" and "Sliding Window" for many extra examples of the monotonic structures.

Next module: **dsa.09 Linked lists**.
