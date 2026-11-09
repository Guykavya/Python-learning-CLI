# dsa.09 Linked lists

## 1. A chain instead of a row

A Python `list` is a **row**: the items sit next to each other, and the item at position 5 is found by jumping straight to position 5. A **linked list** is a **chain**: every item (called a *node*) holds its value and a note that says *where the next node is*. To reach the fifth item you start at the first and follow the notes, four times.

Think of a treasure hunt. The first clue is in your hand. It tells you where the second clue is hidden. The second tells you where the third is. You can never jump to clue 5; you must walk. But there is a gift in return: to **insert** a new clue between clue 2 and clue 3 you do not move anybody. You write one new clue, change the note on clue 2 to point to it, and let the new clue point to the old clue 3. Nothing else changes.

That is the trade:

| Operation | `list` (a row) | Linked list (a chain) |
|---|---|---|
| Get the item at position `i` | `O(1)` | `O(i)`: you must walk |
| Insert or delete at the front | `O(n)` (everything shifts) | `O(1)` |
| Insert or delete in the middle, **when you already hold the node** | `O(n)` (shifting) | `O(1)` (only rewire two notes) |
| Find a value | `O(n)` | `O(n)` |
| Memory per item | one slot | a whole object (value + reference) |

### An honest word first

In everyday Python programs you will almost never write a linked list. The built-in `list` is so fast and so compact that it beats a hand-made chain even in cases where the theory says a chain should win. So why spend a whole module on it?

1. **It teaches pointers (references).** Linked-list problems force you to think about *what a variable really refers to*, and to change links without losing nodes. This skill transfers to trees, graphs, and every data structure that is built from nodes.
2. **It is a staple of interviews.** Reversal, merging, cycle detection and "LRU cache" are asked everywhere.
3. **Real systems use chains inside bigger structures.** `collections.deque` is a chain of small blocks. Hash tables chain items that land in the same bucket. Operating systems chain free memory blocks. An LRU cache is a hash table plus a doubly linked list (section 12).

### What you can do after this module

1. **Build a singly and a doubly linked list from scratch**, with `push`, `pop`, `insert`, `remove`, and iteration, and test it against a Python `list`.
2. **Use a dummy (sentinel) node** to remove special cases at the head.
3. **Reverse a list** (iteratively, recursively, a part of it, or in groups of `k`) **without losing a single node**.
4. **Use fast and slow pointers** to find the middle, detect a cycle, and find where the cycle starts.
5. **Merge sorted lists**, sort a list with merge sort, and reorder or partition a list in place.
6. **Build a stack, a queue and an LRU cache** on top of linked lists, each operation in `O(1)`.
7. **Debug pointer code** with drawings, helper printers, and differential tests.

## 2. Nodes and references

### The node

A node is a tiny object with two fields: the value, and a reference to the next node. The last node's `next` is `None`, which means "the chain ends here".

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

a = ListNode(1)
b = ListNode(2)
c = ListNode(3)
a.next = b
b.next = c
print(a.val, a.next.val, a.next.next.val, a.next.next.next)
```
```text
1 2 3 None
```

Picture it. Each box is an object; an arrow is a reference stored in `next`.

```text
head
 |
 v
[1 | *]--->[2 | *]--->[3 | None]
   a          b          c
```

`a.next.next.val` means: go to `a`, follow `next` to node `b`, follow `next` again to node `c`, read `val`. Reading `a.next.next.next` gives `None`, the end.

### Variables are labels, not boxes

You learned in core.02 that a Python variable does not contain an object; it is a **label stuck onto** an object. Two variables can label the same node. A node does not "know" which variables point to it.

```python
a = ListNode(1)
b = a                       # a second label on the SAME node
b.val = 99
print(a.val, a is b)

c = ListNode(99)            # a different node with an equal value
print(a == c, a is c)       # == falls back to "same object" for plain classes
```
```text
99 True
False False
```

Two things matter for linked lists. First, `is` asks "is it the same node?", which is the question you want when you compare nodes. Second, **if you overwrite the only label that points to a node, and nothing else points to it, you lose that node** (Python will delete it). This is how nodes get lost in pointer code, and it is the number one source of bugs in this module.

### Helper functions you will use everywhere

Typing `ListNode(1, ListNode(2, ListNode(3)))` is tiring. We write three helpers: build a chain from a Python list, turn a chain back into a Python list, and print a chain as an arrow diagram. They are used in every example of this chapter, so copy them to the top of your own file. (The code blocks below do not repeat them.)

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def from_list(values):
    """Build a chain from a Python list and return its head (None if empty)."""
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out

def show(head, limit=20):
    """Arrow diagram. Stops after `limit` nodes, so a cycle cannot hang the program."""
    parts = []
    while head and len(parts) < limit:
        parts.append(str(head.val))
        head = head.next
    if not parts:
        return "None"
    return " -> ".join(parts) + (" -> ..." if head else " -> None")

head = from_list([1, 2, 3, 4])
print(show(head))
print(to_list(head))
print(show(None), to_list(None))
```
```text
1 -> 2 -> 3 -> 4 -> None
[1, 2, 3, 4]
None []
```

`show` has a `limit` on purpose. A list with a cycle would make a plain `while head` loop run forever, and you would see nothing at all. A printer that cannot hang is a debugging tool you can trust.

### The walking pattern

Almost every linked-list function starts with the same loop. Learn it by heart.

```python
def length(head):
    count = 0
    cur = head                  # never move `head` itself: keep the start
    while cur:                  # stop when we fall off the end
        count += 1
        cur = cur.next          # step to the next node
    return count

def get(head, k):
    """Value at position k (0-based), or None if the list is too short."""
    cur = head
    for _ in range(k):
        if cur is None:
            return None
        cur = cur.next
    return cur.val if cur else None

head = from_list([10, 20, 30])
print(length(head), length(None))
print(get(head, 0), get(head, 2), get(head, 3))
```
```text
3 0
10 30 None
```

Two habits are worth building now:

- **Walk with a separate variable** (`cur`), and keep `head` pointing at the start, so you never lose the list.
- **`while cur:` against `while cur.next:`** are different loops. `while cur:` visits every node and ends with `cur = None`. `while cur.next:` stops **on the last node**, which you need when you want to append at the end. If you write `cur.next.next` on a list with fewer than two nodes you get `AttributeError: 'NoneType' object has no attribute 'next'`: the most common error message of this module.

```python
head = from_list([1])
try:
    print(head.next.next)
except AttributeError as e:
    print("AttributeError:", e)
```
```text
AttributeError: 'NoneType' object has no attribute 'next'
```

`head.next` is `None`, and `None` has no `.next`. The fix is never "catch the error": it is to check `if cur and cur.next:` before you reach two steps ahead.

**Predict the output 1.** What do the two prints show?

```python
a = ListNode(1)
b = ListNode(2)
c = ListNode(3)
a.next = b
b.next = c
a.next = c
print(to_list(a))
print(b.val, b.next.val)
```

<details><summary>Answer</summary>

```text
[1, 3]
2 3
```

After `a.next = c`, the chain from `a` is `1 -> 3`: node `b` is no longer reachable *from `a`*. But `b` still exists (the label `b` keeps it alive), and it still points to `c`. So `b.val` is 2 and `b.next.val` is 3. Two chains now share the node `c`. In a real program, if no label were left on `b`, the node would simply be gone.

</details>

**Try it 1.** Write `last_value(head)`, which returns the value of the last node, or `None` for an empty list. Use `while cur.next`.

<details><summary>Answer</summary>

```python
def last_value(head):
    if head is None:
        return None
    cur = head
    while cur.next:              # stops ON the last node
        cur = cur.next
    return cur.val

print(last_value(from_list([4, 5, 6])), last_value(from_list([7])), last_value(None))
```
```text
6 7 None
```

The empty-list check comes first, because `head.next` on `None` would crash. This pattern ("handle empty, then walk to the last node") is how a list without a tail pointer appends at the end.

</details>

## 3. A singly linked list class

Bare nodes are fine for problems, but a class gives a neat interface and lets us keep two extra facts: the **tail** (the last node) and the **size**. With a tail pointer, adding at the back is `O(1)` instead of walking the whole list.

### The design

```text
head                              tail
 |                                  |
 v                                  v
[10 | *]--->[20 | *]--->[30 | None]       size = 3
```

Rules the class must always keep true (its **invariants**):

1. An empty list has `head is None`, `tail is None`, `size == 0`.
2. In a non-empty list, `tail.next is None`, and following `next` from `head` reaches `tail`.
3. `size` equals the number of nodes.

Most bugs break one of these. Every operation must end with all three true.

```python
class LinkedList:
    def __init__(self, values=()):
        self.head = None
        self.tail = None
        self._size = 0
        for v in values:
            self.push_back(v)

    def __len__(self):
        return self._size

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.val
            cur = cur.next

    def __repr__(self):
        return f"LinkedList({list(self)})"

    def push_front(self, val):                    # O(1)
        node = ListNode(val, self.head)           # the new node points at the old head
        self.head = node
        if self.tail is None:                     # the list was empty
            self.tail = node
        self._size += 1

    def push_back(self, val):                     # O(1) thanks to the tail
        node = ListNode(val)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def pop_front(self):                          # O(1)
        if self.head is None:
            raise IndexError("pop from empty list")
        node = self.head
        self.head = node.next
        if self.head is None:                     # we removed the only node
            self.tail = None
        self._size -= 1
        return node.val

    def pop_back(self):                           # O(n): we need the node BEFORE the tail
        if self.head is None:
            raise IndexError("pop from empty list")
        val = self.tail.val
        if self.head is self.tail:
            self.head = self.tail = None
        else:
            cur = self.head
            while cur.next is not self.tail:
                cur = cur.next
            cur.next = None
            self.tail = cur
        self._size -= 1
        return val

    def insert(self, index, val):                 # O(index)
        if not 0 <= index <= self._size:
            raise IndexError("index out of range")
        if index == 0:
            self.push_front(val)
        elif index == self._size:
            self.push_back(val)
        else:
            prev = self.head
            for _ in range(index - 1):
                prev = prev.next                  # stop on the node BEFORE the new position
            prev.next = ListNode(val, prev.next)
            self._size += 1

    def remove(self, val):                        # removes the first match; O(n)
        prev, cur = None, self.head
        while cur:
            if cur.val == val:
                if prev is None:
                    self.head = cur.next          # removing the head
                else:
                    prev.next = cur.next
                if cur is self.tail:
                    self.tail = prev              # removing the last node
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def find(self, val):                          # index of the first match, or -1
        for i, v in enumerate(self):
            if v == val:
                return i
        return -1


lst = LinkedList([10, 20, 30])
lst.push_front(5)
lst.push_back(40)
lst.insert(2, 15)
print(lst, len(lst))
print(lst.pop_front(), lst.pop_back(), lst)
print(lst.remove(20), lst.remove(99), lst, lst.find(30))
```
```text
LinkedList([5, 10, 15, 20, 30, 40]) 6
5 40 LinkedList([10, 15, 20, 30])
True False LinkedList([10, 15, 30]) 2
```

Read the code with a pencil. Three details show why pointer code is tricky:

- **`insert` stops on the node *before* the position.** To put a node at index `i` you must change the `next` of node `i - 1`. A singly linked list cannot go backwards, so you walk to `i - 1` and stop.
- **`pop_back` is `O(n)`** even with a tail pointer, because to remove the last node you must reach the one *before* it, and nothing points backwards. (A doubly linked list fixes this; see section 5.)
- **`remove` keeps a `prev` pointer** (the node before `cur`). When `prev` is `None`, we are at the head, which is a special case; when `cur` is the tail, the tail must move back to `prev`. These are the two places where invariants break.

### Order matters when you rewire

Look at the two lines inside `insert`: `prev.next = ListNode(val, prev.next)`. The new node is created with `next = prev.next` (the old successor) **first**; only then is `prev.next` changed. If you did it the other way round, you would lose the rest of the list.

```python
chain = from_list([1, 2, 3])

# WRONG order: overwrite first, then try to use the old value
node = ListNode(99)
chain.next = node            # the old successor (node 2) is no longer reachable from anywhere
node.next = chain.next       # this now points to node itself!
print(show(chain))
```
```text
1 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> 99 -> ...
```

The result is a cycle `1 -> 99 -> 99 -> ...` (our `show` stops after 20 nodes), and node `2` and node `3` are lost. The right order is: **first make the new node point at what comes next, then point the previous node at the new node.**

```python
chain = from_list([1, 2, 3])
node = ListNode(99)
node.next = chain.next       # 1: new node takes over the rest of the chain
chain.next = node            # 2: the previous node now points at the new node
print(show(chain))
```
```text
1 -> 99 -> 2 -> 3 -> None
```

A good rule: **a link may be overwritten only when its old value is stored somewhere else** (in another node's `next`, or in a variable).

### Trust, but test: a differential test

How do we know that our class is right? Compare it with something we trust: a Python `list` doing the same operations. We generate many random operations with a fixed seed, apply them to both, and compare the contents, the length, and the invariants after every step. This is a **differential test**.

```python
import random

def check(lst, model):
    assert list(lst) == model, (list(lst), model)
    assert len(lst) == len(model)
    if model:
        assert lst.tail.next is None and lst.tail.val == model[-1]
        assert lst.head.val == model[0]
    else:
        assert lst.head is None and lst.tail is None

rng = random.Random(42)
lst, model = LinkedList(), []
for step in range(3000):
    op = rng.choice(["pf", "pb", "popf", "popb", "ins", "rem"])
    if op == "pf":
        v = rng.randint(0, 5); lst.push_front(v); model.insert(0, v)
    elif op == "pb":
        v = rng.randint(0, 5); lst.push_back(v); model.append(v)
    elif op == "popf" and model:
        assert lst.pop_front() == model.pop(0)
    elif op == "popb" and model:
        assert lst.pop_back() == model.pop()
    elif op == "ins":
        i = rng.randint(0, len(model)); v = rng.randint(0, 5)
        lst.insert(i, v); model.insert(i, v)
    elif op == "rem":
        v = rng.randint(0, 5)
        found = v in model
        assert lst.remove(v) == found
        if found:
            model.remove(v)
    check(lst, model)
print("3000 random operations: the linked list always matches the Python list")
```
```text
3000 random operations: the linked list always matches the Python list
```

The values go only from 0 to 5, so there are many repeated values: that is where `remove` could remove the wrong one. If one assertion had failed, the message would show both lists, and you could shrink the test to find the bug. Use this method for every data structure you write.

**Predict the output 2.** What does this print?

```python
lst = LinkedList([1, 2, 3])
lst.remove(3)
lst.push_back(9)
print(lst, lst.tail.val, len(lst))
```

<details><summary>Answer</summary>

```text
LinkedList([1, 2, 9]) 9 3
```

Removing `3` removes the last node, so `remove` must move the tail back to the node holding `2`. If it forgot (`if cur is self.tail: self.tail = prev`), the tail would still point at the removed node, and `push_back(9)` would attach `9` to a node that is no longer in the list: the list would still print `[1, 2]` and the `9` would be lost. The test above would catch that at once.

</details>

## 4. The dummy node: no more special cases for the head

In `remove` we wrote an `if prev is None` branch because the head has nobody before it. This "the first node is different" problem appears in nearly every linked-list function: removing, inserting, merging, partitioning. There is one trick that makes it disappear: put a fake node, called the **dummy** (or **sentinel**), *before* the head.

```text
dummy        head
  |            |
  v            v
[ ? | *]--->[1 | *]--->[2 | *]--->[3 | None]
```

Now every real node, including the first one, has a node before it. The real head is `dummy.next`. At the end you return `dummy.next`, which is correct even if the head was removed or replaced.

### Example: remove all nodes with a given value

**Without a dummy:**

```python
def remove_all_plain(head, target):
    while head and head.val == target:        # first: skip matching nodes at the front
        head = head.next
    cur = head
    while cur and cur.next:
        if cur.next.val == target:
            cur.next = cur.next.next          # unlink the next node
        else:
            cur = cur.next
    return head

print(show(remove_all_plain(from_list([6, 6, 1, 6, 2, 6]), 6)))
```
```text
1 -> 2 -> None
```

**With a dummy:** one loop, no special case.

```python
def remove_all(head, target):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next:
        if prev.next.val == target:
            prev.next = prev.next.next        # unlink; do NOT advance prev
        else:
            prev = prev.next
    return dummy.next

for values, target in (([6, 6, 1, 6, 2, 6], 6), ([7, 7], 7), ([], 6), ([1, 2, 3], 6)):
    print(values, "remove", target, "->", show(remove_all(from_list(values), target)))
```
```text
[6, 6, 1, 6, 2, 6] remove 6 -> 1 -> 2 -> None
[7, 7] remove 7 -> None
[] remove 6 -> None
[1, 2, 3] remove 6 -> 1 -> 2 -> 3 -> None
```

Look at the key line: after unlinking, we **do not advance `prev`**. The new `prev.next` might also match (as in `6, 6`), so it must be checked too. Advance only when nothing was removed. This is a very common source of bugs: advancing in both cases skips a node.

### Where the dummy helps most

| Task | What the dummy does |
|---|---|
| Delete nodes (maybe the head) | the head has a "previous" node |
| Build a new list node by node | the new list's head is `dummy.next`; no "is this the first node?" test |
| Merge two lists | the result starts at `dummy.next` |
| Insert into a sorted list | inserting before the first node needs no special case |
| Partition a list | two dummies, one for each part |

We already used the trick in `from_list`: `dummy`, `tail`, and `return dummy.next`. That is the standard way to build a list from scratch.

### Example: insert into a sorted list

```python
def insert_sorted(head, val):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next and prev.next.val < val:
        prev = prev.next                      # stop on the last node smaller than val
    prev.next = ListNode(val, prev.next)
    return dummy.next

head = from_list([2, 4, 6])
for v in (5, 1, 9):
    head = insert_sorted(head, v)
    print(show(head))
```
```text
2 -> 4 -> 5 -> 6 -> None
1 -> 2 -> 4 -> 5 -> 6 -> None
1 -> 2 -> 4 -> 5 -> 6 -> 9 -> None
```

Inserting `1` goes before the head; inserting `9` goes after the tail. The same four lines handle the head, the middle and the tail.

**Try it 2.** Using a dummy node, write `delete_nth(head, n)` that deletes the node at index `n` (0-based) and returns the new head. If `n` is out of range, return the list unchanged.

<details><summary>Answer</summary>

```python
def delete_nth(head, n):
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(n):
        if prev.next is None:
            return dummy.next               # out of range
        prev = prev.next                    # after n steps, prev is the node BEFORE index n
    if prev.next is not None:
        prev.next = prev.next.next
    return dummy.next

for n in (0, 1, 2, 5):
    print(n, show(delete_nth(from_list([10, 20, 30]), n)))
```
```text
0 20 -> 30 -> None
1 10 -> 30 -> None
2 10 -> 20 -> None
5 10 -> 20 -> 30 -> None
```

With the dummy, `n = 0` is no special case: after zero steps `prev` is the dummy, and `prev.next` is the head. The check `prev.next is not None` covers `n` equal to the length (one past the end).

</details>

## 5. Doubly linked lists

In a singly linked list you can only walk forward. That caused two problems: `pop_back` had to walk the whole list to find the node before the tail, and to delete a node you needed a `prev` pointer from the walk. A **doubly linked list** gives each node a second reference, `prev`, to the node before it.

```text
        +--------+       +--------+       +--------+
None <--| prev   |<------| prev   |<------| prev   |
        | 10     |       | 20     |       | 30     |
        | next   |------>| next   |------>| next   |--> None
        +--------+       +--------+       +--------+
```

Now every node knows both neighbours. The reward: **if you hold a node, you can remove it in `O(1)`** with no walking, because `node.prev` is right there. The price: one more reference per node (more memory), and **twice as many links to keep correct**.

### Two sentinels instead of `None` checks

With `None` at both ends, every operation needs "is this the first node? the last node? the only node?" tests. The dummy-node idea from section 4 helps again: use **two sentinel nodes**, a `head` before the first real node and a `tail` after the last. They never hold data and are never removed. The list is empty when `head.next is tail`.

```text
 head(sentinel) <-> 10 <-> 20 <-> 30 <-> tail(sentinel)
```

Now *every real node always has a real node (or a sentinel) on both sides*, so the code that links and unlinks never needs an `if`.

```python
class DNode:
    def __init__(self, val=None):
        self.val = val
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = DNode()                  # sentinel before the first item
        self.tail = DNode()                  # sentinel after the last item
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        cur = self.head.next
        while cur is not self.tail:
            yield cur.val
            cur = cur.next

    def reversed_values(self):
        cur = self.tail.prev
        while cur is not self.head:
            yield cur.val
            cur = cur.prev

    def __repr__(self):
        return f"DoublyLinkedList({list(self)})"

    def insert_after(self, node, val):       # O(1): the heart of the class
        new = DNode(val)
        new.prev = node                      # 1. the new node looks backwards ...
        new.next = node.next                 # 2. ... and forwards, using the OLD links
        node.next.prev = new                 # 3. the next node looks back at the new one
        node.next = new                      # 4. the previous node looks forward to it
        self._size += 1
        return new

    def remove_node(self, node):             # O(1) when you hold the node
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None         # cut the loose node free
        self._size -= 1
        return node.val

    def push_front(self, val):
        return self.insert_after(self.head, val)

    def push_back(self, val):
        return self.insert_after(self.tail.prev, val)

    def pop_front(self):
        if self._size == 0:
            raise IndexError("pop from empty list")
        return self.remove_node(self.head.next)

    def pop_back(self):                      # O(1) now: no walking
        if self._size == 0:
            raise IndexError("pop from empty list")
        return self.remove_node(self.tail.prev)

    def node_at(self, index):                # O(n): finding a node still needs a walk
        cur = self.head.next
        for _ in range(index):
            cur = cur.next
        return cur


d = DoublyLinkedList()
for x in (20, 30):
    d.push_back(x)
d.push_front(10)
middle = d.node_at(1)
d.insert_after(middle, 25)
print(d, len(d))
print(list(d.reversed_values()))
print(d.remove_node(middle), d.pop_back(), d.pop_front(), d)
```
```text
DoublyLinkedList([10, 20, 25, 30]) 4
[30, 25, 20, 10]
20 30 10 DoublyLinkedList([25])
```

Look at `insert_after`: it has **four link changes**, and their order matters in the same way as in the singly linked case. Steps 1 and 2 set the new node's own links, using the existing neighbours. Only then do steps 3 and 4 change the neighbours. If you do step 4 first (`node.next = new`), you have lost the reference to the old next node, and step 2 cannot find it.

### Is it right? A differential test

We compare with `collections.deque` (which supports the same operations) and also check the links in **both directions** after every step.

```python
from collections import deque
import random

def check(dll, model):
    assert list(dll) == list(model), (list(dll), list(model))
    assert list(dll.reversed_values()) == list(reversed(model))
    assert len(dll) == len(model)
    assert dll.head.next.prev is dll.head and dll.tail.prev.next is dll.tail

rng = random.Random(8)
dll, model = DoublyLinkedList(), deque()
for _ in range(3000):
    op = rng.choice(["pf", "pb", "popf", "popb", "rem"])
    if op == "pf":
        v = rng.randint(0, 9); dll.push_front(v); model.appendleft(v)
    elif op == "pb":
        v = rng.randint(0, 9); dll.push_back(v); model.append(v)
    elif op == "popf" and model:
        assert dll.pop_front() == model.popleft()
    elif op == "popb" and model:
        assert dll.pop_back() == model.pop()
    elif op == "rem" and model:
        i = rng.randrange(len(model))
        assert dll.remove_node(dll.node_at(i)) == model[i]
        del model[i]
    check(dll, model)
print("3000 random operations agree with collections.deque")
```
```text
3000 random operations agree with collections.deque
```

### Singly or doubly?

| | Singly linked | Doubly linked |
|---|---|---|
| Reference per node | 1 | 2 |
| Walk backwards | no | yes |
| Remove the node you hold | `O(n)` (find the previous one) | `O(1)` |
| `pop_back` | `O(n)` | `O(1)` |
| Simple to write | yes | more links to keep right |
| Used in | stacks, interview problems on reversal and merging | LRU caches, `deque`, undo history, text editors |

**Try it 3.** What is wrong with this `remove_node`, and what would happen to the list `10 <-> 20 <-> 30` if you called it on node `20`?

```python
def remove_node_bad(self, node):
    node.prev.next = node.next
    self._size -= 1
    return node.val
```

<details><summary>Answer</summary>

It fixes only the forward link. After `remove_node_bad(node20)`, walking forward gives `10 -> 30`, but `30.prev` still points to the removed node `20`. Walking backwards from the tail gives `30 -> 20 -> 10`: the removed node is still in the chain. The two directions disagree, which is the typical doubly-linked bug. The fix is the second line, `node.next.prev = node.prev`, which a differential test with `reversed_values()` would catch at once.

```python
d = DoublyLinkedList()
for x in (10, 20, 30):
    d.push_back(x)
node20 = d.node_at(1)
node20.prev.next = node20.next             # the buggy version stops here
print(list(d), list(d.reversed_values()))
```
```text
[10, 30] [30, 20, 10]
```

</details>

## 6. Reversing a list

Reversing is **the** linked-list problem. The idea is simple: every arrow `a -> b` must become `b -> a`. The difficulty is doing it **without losing the rest of the list** while you flip arrows.

### Iterative reversal with three variables

Keep three references while you walk:

- `prev`: the head of the part that is already reversed (starts as `None`, the end of the new list),
- `cur`: the node being flipped,
- `nxt`: the node after `cur`, saved **before** we flip `cur`'s arrow.

At each step: save `nxt = cur.next`; flip `cur.next = prev`; move forward `prev = cur`, `cur = nxt`.

```python
def reverse_list(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next          # 1. save the rest of the list
        cur.next = prev         # 2. flip the arrow
        prev = cur              # 3. the reversed part now starts at cur
        cur = nxt               # 4. move on
    return prev                 # prev is the new head

print(show(reverse_list(from_list([1, 2, 3, 4]))))
print(show(reverse_list(from_list([7]))), show(reverse_list(None)))
```
```text
4 -> 3 -> 2 -> 1 -> None
7 -> None None
```

Watch the state after each step. The helper prints the reversed part and the part that is still waiting.

```python
def reverse_traced(head):
    prev, cur = None, head
    print(f"start   reversed: {show(prev):<26} rest: {show(cur)}")
    step = 0
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
        step += 1
        print(f"step {step}  reversed: {show(prev):<26} rest: {show(cur)}")
    return prev

reverse_traced(from_list([1, 2, 3, 4]))
```
```text
start   reversed: None                       rest: 1 -> 2 -> 3 -> 4 -> None
step 1  reversed: 1 -> None                  rest: 2 -> 3 -> 4 -> None
step 2  reversed: 2 -> 1 -> None             rest: 3 -> 4 -> None
step 3  reversed: 3 -> 2 -> 1 -> None        rest: 4 -> None
step 4  reversed: 4 -> 3 -> 2 -> 1 -> None   rest: None
```

The two parts always add up to the whole list: nothing is lost, nothing is counted twice. This is the **loop invariant** of reversal: *the nodes before `cur` are already reversed and start at `prev`; the nodes from `cur` are untouched.* When `cur` becomes `None`, everything is reversed and `prev` is the new head.

### Why `nxt` must be saved first

What if you forget it and write `cur = cur.next` after flipping?

```python
def reverse_lost(head):
    prev, cur = None, head
    while cur:
        cur.next = prev          # flipped before saving the old next
        prev = cur
        cur = cur.next           # BUG: cur.next is now prev, not the old next
    return prev

print(show(reverse_lost(from_list([1, 2, 3]))))
```
```text
1 -> None
```

After the first flip, node `1` points to `None`, so `cur = cur.next` is `None` and the loop stops. Nodes `2` and `3` are lost. The rule from section 3 again: **do not overwrite a link until its old value is saved.**

### Recursive reversal

Think recursively (dsa.07): "reverse the rest of the list, then attach the first node at the end." If the list is `1 -> 2 -> 3`: the rest `2 -> 3` is reversed to `3 -> 2`; node `1` must go after `2`. And `2` is `head.next`, so `head.next.next = head` does that; then `head.next = None` cuts the old arrow.

```python
def reverse_rec(head):
    if head is None or head.next is None:       # base case: 0 or 1 node
        return head
    new_head = reverse_rec(head.next)           # reverse everything after head
    head.next.next = head                       # the old next now points back at head
    head.next = None                            # head becomes the tail
    return new_head

print(show(reverse_rec(from_list([1, 2, 3, 4]))))
```
```text
4 -> 3 -> 2 -> 1 -> None
```

It is short and pretty, but there is a price: the recursion is as deep as the list, so a long list hits Python's recursion limit (dsa.07, section 2).

```python
big = from_list(range(5000))
try:
    reverse_rec(big)
except RecursionError:
    print("recursive: RecursionError on 5000 nodes")

print("iterative:", reverse_list(from_list(range(5000))).val)
```
```text
recursive: RecursionError on 5000 nodes
iterative: 4999
```

In practice, write the iterative version. Know the recursive one for interviews, because the "`head.next.next = head`" line is a popular question.

### Reverse only part of the list

Reverse the nodes from position `left` to position `right` (1-based, inclusive): `1 -> 2 -> 3 -> 4 -> 5` with `left = 2, right = 4` becomes `1 -> 4 -> 3 -> 2 -> 5`. Use a dummy node, walk to the node just before the part (`prev`), and then repeatedly **move the node after `cur` to the front of the part**.

```python
def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(left - 1):
        prev = prev.next                 # the node just before position `left`
    cur = prev.next                      # the first node of the part; it will end up last
    for _ in range(right - left):
        nxt = cur.next                   # take the node after cur ...
        cur.next = nxt.next              # ... cut it out of its place ...
        nxt.next = prev.next             # ... and put it in front of the part
        prev.next = nxt
    return dummy.next

print(show(reverse_between(from_list([1, 2, 3, 4, 5]), 2, 4)))
print(show(reverse_between(from_list([1, 2, 3, 4, 5]), 1, 5)))
print(show(reverse_between(from_list([5]), 1, 1)))
```
```text
1 -> 4 -> 3 -> 2 -> 5 -> None
5 -> 4 -> 3 -> 2 -> 1 -> None
5 -> None
```

Note that `cur` never moves: it is the first node of the part, and as the others are pulled to the front, `cur` slides to the end of the part. That is why the loop needs no `cur = ...` update.

### Reverse in groups of k

Reverse the nodes `k` at a time; if fewer than `k` nodes remain at the end, leave them as they are. For `1 -> 2 -> 3 -> 4 -> 5`: with `k = 2` the answer is `2 -> 1 -> 4 -> 3 -> 5`, with `k = 3` it is `3 -> 2 -> 1 -> 4 -> 5`.

For each group: (1) check that `k` nodes really exist, (2) reverse them with the usual loop, but let the group's *first* node end up pointing to the first node of the *next* group, (3) connect the previous group's tail to the new group head.

```python
def get_kth(node, k):
    while node and k > 0:
        node = node.next
        k -= 1
    return node

def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy                       # the node just before the current group
    while True:
        kth = get_kth(group_prev, k)         # the last node of the group, or None
        if kth is None:
            break                            # fewer than k nodes remain: stop
        group_next = kth.next                # the first node after the group
        prev, cur = group_next, group_prev.next
        while cur is not group_next:         # reverse the group; its first node will point to group_next
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        old_first = group_prev.next          # now the last node of the reversed group
        group_prev.next = kth                # the previous part links to the new group head
        group_prev = old_first
    return dummy.next

for k in (2, 3, 1, 6):
    print(k, show(reverse_k_group(from_list([1, 2, 3, 4, 5]), k)))
```
```text
2 2 -> 1 -> 4 -> 3 -> 5 -> None
3 3 -> 2 -> 1 -> 4 -> 5 -> None
1 1 -> 2 -> 3 -> 4 -> 5 -> None
6 1 -> 2 -> 3 -> 4 -> 5 -> None
```

The trick is `prev = group_next` as the starting value: instead of `None`, the reversed group's last arrow points straight at the rest of the list. `k = 1` changes nothing, and `k` larger than the length changes nothing. Swapping nodes in pairs is just `reverse_k_group(head, 2)`.

### Check the four against list operations

```python
import random

rng = random.Random(21)
ok = True
for _ in range(400):
    a = [rng.randint(0, 9) for _ in range(rng.randint(0, 9))]
    ok &= to_list(reverse_list(from_list(a))) == a[::-1]
    ok &= to_list(reverse_rec(from_list(a))) == a[::-1]
    if a:
        l = rng.randint(1, len(a)); r = rng.randint(l, len(a))
        ok &= to_list(reverse_between(from_list(a), l, r)) == a[:l - 1] + a[l - 1:r][::-1] + a[r:]
    k = rng.randint(1, 4)
    expected = []
    for i in range(0, len(a), k):
        chunk = a[i:i + k]
        expected += chunk[::-1] if len(chunk) == k else chunk
    ok &= to_list(reverse_k_group(from_list(a), k)) == expected
print("400 random lists: all four reversals match the list version:", bool(ok))
```
```text
400 random lists: all four reversals match the list version: True
```

**Predict the output 3.** What does `reverse_between` print for `left = 1, right = 3` on `[1, 2, 3, 4]`, and why does it need no special case for `left = 1`?

```python
print(show(reverse_between(from_list([1, 2, 3, 4]), 1, 3)))
```

<details><summary>Answer</summary>

```text
3 -> 2 -> 1 -> 4 -> None
```

The first three nodes are reversed, `4` stays. For `left = 1` the loop `for _ in range(left - 1)` runs zero times, so `prev` stays at the dummy, and `dummy.next` is updated like any other `prev.next`. The dummy is the reason there is no special case; without it, the head would change and you would have to handle that separately.

</details>

**Try it 4.** Reverse a list with a stack (a Python list): push all the values, then pop them while building a new list. What is the time and the extra space compared with `reverse_list`?

<details><summary>Answer</summary>

```python
def reverse_with_stack(head):
    stack = []
    cur = head
    while cur:
        stack.append(cur.val)
        cur = cur.next
    return from_list(reversed(stack))

print(show(reverse_with_stack(from_list([1, 2, 3, 4]))))
```
```text
4 -> 3 -> 2 -> 1 -> None
```

Time: `O(n)`, the same. Extra space: `O(n)` for the stack and for the new nodes, where the in-place `reverse_list` needs only `O(1)` extra space and creates no new nodes. Interview problems almost always ask for the in-place version.

</details>

## 7. Fast and slow pointers

A powerful idea: walk the list with **two pointers at different speeds**. The `slow` pointer moves one node per step; the `fast` pointer moves two. Because the fast pointer covers twice the distance, when it reaches the end the slow pointer is exactly in the middle. And if the list has a loop, the fast pointer will catch the slow one from behind. Both facts need only `O(1)` extra space and a single pass.

### The middle of a list

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next             # one step
        fast = fast.next.next        # two steps
    return slow

for n in range(1, 7):
    print(n, "nodes -> middle value", middle(from_list(range(1, n + 1))).val)
```
```text
1 nodes -> middle value 1
2 nodes -> middle value 2
3 nodes -> middle value 2
4 nodes -> middle value 3
5 nodes -> middle value 3
6 nodes -> middle value 4
```

For an odd number of nodes there is one middle. For an even number there are two, and this version returns the **second** one (`4` nodes give the 3rd). If you need the first middle instead (for example, to cut the list in two equal halves), change the loop condition to `while fast.next and fast.next.next`.

```python
def first_middle(head):
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    return slow

print([first_middle(from_list(range(1, n + 1))).val for n in range(1, 7)])
```
```text
[1, 1, 2, 2, 3, 3]
```

Always test your middle function on lists of length 1, 2, 3 and 4: the even-length case is where mistakes live.

### Detecting a cycle (Floyd's tortoise and hare)

A list has a **cycle** if some node's `next` points back to an earlier node, so the chain never ends. A plain `while cur:` loop would run forever.

The idea: run slow and fast from the head. If there is no cycle, `fast` reaches `None` and we answer "no". If there is a cycle, both pointers eventually enter it. Inside the cycle the distance from `slow` to `fast` (counted along the direction of the arrows) **shrinks by exactly 1 each step**, because `fast` gains one node per step. It cannot jump over `slow`, so sooner or later the distance is 0: they meet.

First, a helper that builds a list whose tail points back to the node at index `pos` (use `-1` for no cycle).

```python
def make_cycle(values, pos):
    head = from_list(values)
    if pos < 0 or head is None:
        return head, None
    target = head
    for _ in range(pos):
        target = target.next
    tail = head
    while tail.next:
        tail = tail.next
    tail.next = target                   # close the loop
    return head, target

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

for values, pos in (([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], -1), ([1], 0), ([1, 2], 0), ([], -1)):
    head, _ = make_cycle(values, pos)
    print(values, "cycle back to index", pos, "->", has_cycle(head))
```
```text
[1, 2, 3, 4, 5] cycle back to index 2 -> True
[1, 2, 3, 4, 5] cycle back to index -1 -> False
[1] cycle back to index 0 -> True
[1, 2] cycle back to index 0 -> True
[] cycle back to index -1 -> False
```

Watch the chase. Each line shows the positions (as indices) of the two pointers.

```python
def chase(values, pos):
    head, _ = make_cycle(values, pos)
    index, cur, i = {}, head, 0
    while cur and id(cur) not in index:
        index[id(cur)] = i
        cur, i = cur.next, i + 1
    slow = fast = head
    step = 0
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        step += 1
        print(f"step {step}: slow at {index[id(slow)]}, fast at {index[id(fast)]}")
        if slow is fast:
            print("they meet")
            return

chase([0, 1, 2, 3, 4, 5], 2)         # 6 nodes; the tail points back to index 2
```
```text
step 1: slow at 1, fast at 2
step 2: slow at 2, fast at 4
step 3: slow at 3, fast at 2
step 4: slow at 4, fast at 4
they meet
```

### The alternative with a set, and why we prefer two pointers

You could store each visited node in a `set` and stop when you see one twice. It works, but costs `O(n)` memory. Floyd's method needs `O(1)`.

```python
def has_cycle_set(head):
    seen = set()
    cur = head
    while cur:
        if cur in seen:
            return True
        seen.add(cur)
        cur = cur.next
    return False

import random
rng = random.Random(4)
ok = True
for _ in range(300):
    n = rng.randint(0, 10)
    pos = rng.randint(-1, n - 1) if n else -1
    head, _ = make_cycle(list(range(n)), pos)
    ok &= has_cycle(head) == has_cycle_set(head) == (pos >= 0)
print("two pointers, set, and the expected answer agree:", bool(ok))
```
```text
two pointers, set, and the expected answer agree: True
```

### Where does the cycle start?

After the pointers meet, do this: put one pointer back at the head, and move **both one step at a time**. They meet again exactly at the first node of the cycle.

Why? Let `a` be the number of steps from the head to the cycle start, and `c` the length of the cycle. When `slow` has walked `a + b` steps, it is `b` steps inside the cycle, and that is where they meet. `fast` has walked twice as far: `2(a + b)`. The difference between them, `a + b`, is a whole number of laps: `a + b = m * c`. Rearranged: `a = m * c - b = (m - 1) * c + (c - b)`. Now `c - b` is exactly the number of steps from the meeting point to the cycle start (going forward). So walking `a` steps from the meeting point also lands at the start (the extra `(m - 1)` laps bring you back to the same place). The pointer from the head also needs `a` steps. So both arrive at the start together.

```python
def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            ptr = head
            while ptr is not slow:
                ptr = ptr.next
                slow = slow.next
            return ptr                    # the first node of the cycle
    return None

ok = True
for n in range(1, 9):
    for pos in range(n):
        head, target = make_cycle(list(range(n)), pos)
        ok &= cycle_start(head) is target
print("start found for every size and position:", bool(ok))
print(cycle_start(from_list([1, 2, 3])))
```
```text
start found for every size and position: True
None
```

### The length of the cycle

Once the pointers meet, keep one fixed and move the other until it comes back. The number of steps is the cycle length.

```python
def cycle_length(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            count, cur = 1, slow.next
            while cur is not slow:
                cur = cur.next
                count += 1
            return count
    return 0

head, _ = make_cycle(list(range(7)), 3)           # nodes 3..6 form the cycle
print(cycle_length(head), cycle_length(from_list([1, 2, 3])))
```
```text
4 0
```

### The same idea without any list: happy numbers

Replace a number by the sum of the squares of its digits, again and again. Some numbers reach `1` ("happy"); others fall into a loop that never contains `1`. There is no linked list here, but the sequence `n -> f(n) -> f(f(n)) ...` has exactly the same shape (a chain that may end or loop), so the same two-pointer idea detects the loop with no memory.

```python
def digit_square_sum(n):
    return sum(int(d) ** 2 for d in str(n))

def is_happy(n):
    slow, fast = n, digit_square_sum(n)
    while fast != 1 and slow != fast:
        slow = digit_square_sum(slow)
        fast = digit_square_sum(digit_square_sum(fast))
    return fast == 1

print([n for n in range(1, 51) if is_happy(n)])
print(is_happy(19), is_happy(2))
```
```text
[1, 7, 10, 13, 19, 23, 28, 31, 32, 44, 49]
True False
```

### A cycle hidden in an array: find the duplicate

An array of `n + 1` numbers holds values between `1` and `n`, so at least one value appears twice. Without changing the array and with `O(1)` extra space, find a duplicate. Treat each index `i` as a node whose "next" is `nums[i]`. Because two indices point to the same value, there is a cycle, and the **cycle start is the duplicated value** (two arrows enter it). Index `0` is never inside the cycle (nobody points to `0`), so it plays the role of the head.

```python
def find_duplicate(nums):
    slow = fast = 0
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    ptr = 0
    while ptr != slow:
        ptr = nums[ptr]
        slow = nums[slow]
    return ptr

print(find_duplicate([1, 3, 4, 2, 2]), find_duplicate([3, 1, 3, 4, 2]), find_duplicate([2, 2, 2, 2, 2]))
```
```text
2 3 2
```

This is a famous example of how a list technique solves an array problem. The array version of `slow = slow.next` is `slow = nums[slow]`.

**Predict the output 4.** For the list `1 -> 2 -> 3 -> 4 -> 5 -> 6` (no cycle), what do `middle` and `first_middle` return?

<details><summary>Answer</summary>

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow

def first_middle(head):
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    return slow

head = from_list([1, 2, 3, 4, 5, 6])
print(middle(head).val, first_middle(head).val)
```
```text
4 3
```

Six nodes have two middle nodes, the 3rd (value 3) and the 4th (value 4). `middle` returns the second (4) because `fast` moves while it has a node and a next node; `first_middle` stops one step earlier and returns the first (3).

</details>

**Try it 5.** Write `kth_from_end(head, k)` (1-based: `k = 1` is the last node) using two pointers that start `k` nodes apart, moving at the **same** speed. Return `None` if the list is shorter than `k`.

<details><summary>Answer</summary>

```python
def kth_from_end(head, k):
    lead = head
    for _ in range(k):
        if lead is None:
            return None                  # fewer than k nodes
        lead = lead.next                 # move the lead pointer k steps ahead
    follow = head
    while lead:                          # when lead falls off the end, follow is k from the end
        lead = lead.next
        follow = follow.next
    return follow.val

head = from_list([10, 20, 30, 40, 50])
print(kth_from_end(head, 1), kth_from_end(head, 2), kth_from_end(head, 5), kth_from_end(head, 6))
```
```text
50 40 10 None
```

This is the "two pointers with a gap" cousin of fast and slow. The gap between them stays `k`, so when the front one is past the end, the back one is `k` nodes from the end. The same idea removes the n-th node from the end (next section).

</details>

## 8. Merging and sorting

### Merge two sorted lists

Two lists are sorted. Make one sorted list from them. The idea is the "merge" step of merge sort: compare the two front nodes, take the smaller one, and repeat. With a dummy node and a `tail` pointer that always points to the last node of the result, the code has no special cases.

Notice that we create **no new nodes**: we only rewire the existing ones. The result is made of the nodes of `a` and `b`, so the inputs are used up.

```python
def merge_two(a, b):
    dummy = ListNode()
    tail = dummy
    while a and b:
        if a.val <= b.val:           # <= takes from `a` first on ties: the merge is stable
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a or b               # one list is empty: attach the whole rest of the other
    return dummy.next

print(show(merge_two(from_list([1, 2, 4]), from_list([1, 3, 4]))))
print(show(merge_two(None, from_list([0]))), show(merge_two(None, None)))
```
```text
1 -> 1 -> 2 -> 3 -> 4 -> 4 -> None
0 -> None None
```

Two lines deserve a second look. `tail.next = a or b` attaches the *remaining nodes in one step*: when one list is exhausted, the rest of the other is already sorted and linked, so we do not copy it node by node. And the cost is `O(len(a) + len(b))` time with `O(1)` extra space.

```python
x, y = from_list([1, 5]), from_list([2, 6])
x_nodes = [x, x.next]
merged = merge_two(x, y)
print(show(merged))
print("same node objects reused:", merged is x_nodes[0], merged.next.next is x_nodes[1])
```
```text
1 -> 2 -> 5 -> 6 -> None
same node objects reused: True True
```

### Merge k sorted lists

There are `k` sorted lists, with `N` nodes in total. Merging them one after another costs up to `O(k * N)`, because the result gets longer and longer and is scanned again each time. Two better ways, both `O(N log k)`:

**1. A heap.** Keep the current front node of each list in a min-heap. Pop the smallest, append it to the result, push the next node of the same list.

One trap: if two nodes have equal values, `heapq` compares the *next* element of the tuple, which would be the node, and nodes cannot be compared.

```python
import heapq

h = []
heapq.heappush(h, (1, ListNode(1)))
try:
    heapq.heappush(h, (1, ListNode(1)))
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
```

The fix is a **tie-breaker** in the middle of the tuple: the index of the list. Two entries can never have the same `(value, index)` pair, because each list has only one node in the heap at a time.

```python
import heapq

def merge_k_heap(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = ListNode()
    tail = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

**2. Divide and conquer.** Merge the lists in pairs, then merge the results in pairs, and so on. There are `log k` rounds, and each round touches every node once.

```python
def merge_k_pairs(lists):
    if not lists:
        return None
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            b = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(lists[i], b))
        lists = merged
    return lists[0]

data = [[1, 4, 5], [1, 3, 4], [2, 6], [], [0, 9]]
print(show(merge_k_heap([from_list(x) for x in data])))
print(show(merge_k_pairs([from_list(x) for x in data])))
print(sorted(v for x in data for v in x))
```
```text
0 -> 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6 -> 9 -> None
0 -> 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6 -> 9 -> None
[0, 1, 1, 2, 3, 4, 4, 5, 6, 9]
```

The heap method keeps only `k` nodes in the heap (`O(k)` extra space). The pairwise method uses `O(1)` extra space for the nodes. Either is a good answer; the heap is shorter to write when you know `heapq`.

### Sort a linked list: merge sort

Sorting an array with quicksort needs random access. A linked list has none, but it has something an array lacks: **merging two sorted pieces costs `O(1)` extra space**. So merge sort is the natural choice:

1. If there is 0 or 1 node, it is already sorted.
2. Find the middle with slow and fast pointers, and **cut** the list in two there.
3. Sort each half (recursively).
4. Merge the sorted halves.

```python
def sort_list(head):
    if head is None or head.next is None:
        return head
    slow, fast = head, head.next          # starting fast one step ahead makes slow the FIRST middle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                      # the cut: without it the halves would not be separate
    return merge_two(sort_list(head), sort_list(second))

print(show(sort_list(from_list([4, 2, 1, 3]))))
print(show(sort_list(from_list([-1, 5, 3, 4, 0]))))
```
```text
1 -> 2 -> 3 -> 4 -> None
-1 -> 0 -> 3 -> 4 -> 5 -> None
```

Starting `fast` at `head.next` matters. With both starting at `head`, a list of two nodes would have `slow` end on the second node; the "second half" would be empty and the "first half" would still have two nodes: the recursion would never shrink and never stop. Starting `fast` one step ahead makes `slow` the *first* middle, so both halves are strictly shorter than the whole list.

Time `O(n log n)`. Space `O(log n)` for the recursion (the depth is `log n`, so no recursion-limit problem even for a million nodes).

```python
import random

rng = random.Random(2)
values = [rng.randint(0, 10**6) for _ in range(20000)]
print(to_list(sort_list(from_list(values))) == sorted(values))
```
```text
True
```

**Predict the output 5.** What happens to the original `head` variable after `sort_list`?

```python
head = from_list([3, 1, 2])
sorted_head = sort_list(head)
print(show(sorted_head))
print(show(head))
```

<details><summary>Answer</summary>

```text
1 -> 2 -> 3 -> None
3 -> None
```

The sort rewires the existing nodes. `head` still refers to the node with value 3, which is now the **last** node of the sorted list, so `show(head)` prints just `3 -> None`. Moral: after a function that rewires nodes, always use the **returned** head and not your old variable. This is the rule behind "return `dummy.next`".

</details>

**Try it 6.** Merge two sorted lists *recursively* in four lines. What is the cost in space?

<details><summary>Answer</summary>

```python
def merge_rec(a, b):
    if a is None or b is None:
        return a or b
    if a.val <= b.val:
        a.next = merge_rec(a.next, b)
        return a
    b.next = merge_rec(a, b.next)
    return b

print(show(merge_rec(from_list([1, 2, 4]), from_list([1, 3, 4]))))
```
```text
1 -> 1 -> 2 -> 3 -> 4 -> 4 -> None
```

It is elegant, but the recursion is as deep as the total number of nodes, so the space is `O(n)` and a long list hits the recursion limit. The iterative version with a dummy node uses `O(1)` space.

</details>

## 9. Classic rearrangements

This section collects the standard problems. Each one combines the tools you already have: the dummy node, two pointers, reversal and merging.

### Remove the n-th node from the end

Use a gap of `n` between two pointers (as in `kth_from_end`), but starting at a dummy, so removing the head is not special. We need the node **before** the one to remove, so `lead` goes `n + 1` steps ahead.

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    lead = follow = dummy
    for _ in range(n + 1):
        lead = lead.next                 # open a gap of n+1 nodes
    while lead:
        lead = lead.next
        follow = follow.next             # follow stops on the node BEFORE the one to remove
    follow.next = follow.next.next
    return dummy.next

for n in (1, 2, 5):
    print(n, show(remove_nth_from_end(from_list([1, 2, 3, 4, 5]), n)))
print(show(remove_nth_from_end(from_list([1]), 1)))
```
```text
1 1 -> 2 -> 3 -> 4 -> None
2 1 -> 2 -> 3 -> 5 -> None
5 2 -> 3 -> 4 -> 5 -> None
None
```

One pass, `O(1)` space. Removing the 5th from the end of a 5-node list removes the head; the dummy handles it.

### Is the list a palindrome? (in `O(1)` space)

Copy the values to a Python list and compare with the reversed list: easy, but `O(n)` space. The pointer solution: find the middle, reverse the second half in place, compare the two halves, and (politely) reverse the second half back.

```python
def is_palindrome_list(head):
    if head is None or head.next is None:
        return True
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next            # slow ends on the first middle
    second = reverse_list(slow.next)     # reverse the second half
    p1, p2 = head, second
    result = True
    while p2:                            # the second half is never longer than the first
        if p1.val != p2.val:
            result = False
            break
        p1, p2 = p1.next, p2.next
    slow.next = reverse_list(second)     # restore the list
    return result

for values in ([1, 2, 2, 1], [1, 2, 3, 2, 1], [1, 2], [1], [], [1, 2, 3, 1]):
    head = from_list(values)
    print(values, is_palindrome_list(head), "unchanged:", to_list(head) == values)
```
```text
[1, 2, 2, 1] True unchanged: True
[1, 2, 3, 2, 1] True unchanged: True
[1, 2] False unchanged: True
[1] True unchanged: True
[] True unchanged: True
[1, 2, 3, 1] False unchanged: True
```

For an odd length, the middle node stays in the first half and is not compared with anything, which is correct. Restoring the list is good manners: a function that answers a yes/no question should not damage its input.

### Reorder: first, last, second, second-last ...

`1 -> 2 -> 3 -> 4 -> 5` becomes `1 -> 5 -> 2 -> 4 -> 3`. Three tools in a row: **find the middle**, **reverse the second half**, **weave** the two halves together.

```python
def reorder_list(head):
    if head is None or head.next is None:
        return
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = reverse_list(slow.next)     # the second half, reversed
    slow.next = None                     # cut the first half off
    first = head
    while second:
        n1, n2 = first.next, second.next # save both next nodes before rewiring
        first.next = second
        second.next = n1
        first, second = n1, n2

for values in ([1, 2, 3, 4], [1, 2, 3, 4, 5], [1, 2], [1]):
    head = from_list(values)
    reorder_list(head)
    print(values, "->", show(head))
```
```text
[1, 2, 3, 4] -> 1 -> 4 -> 2 -> 3 -> None
[1, 2, 3, 4, 5] -> 1 -> 5 -> 2 -> 4 -> 3 -> None
[1, 2] -> 1 -> 2 -> None
[1] -> 1 -> None
```

This function changes the list in place and returns nothing: the head does not change (the first node stays first). Compare with `reverse_list`, which returns a new head.

### Rotate right by k

`1 -> 2 -> 3 -> 4 -> 5` rotated right by 2 is `4 -> 5 -> 1 -> 2 -> 3`. Make the list a ring (tail points to head), then break the ring at the right place.

```python
def rotate_right(head, k):
    if head is None or head.next is None:
        return head
    n, tail = 1, head
    while tail.next:
        tail = tail.next
        n += 1                           # count the nodes and find the tail
    k %= n                               # rotating by n changes nothing
    if k == 0:
        return head
    tail.next = head                     # close the ring
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next         # the node that becomes the last one
    new_head = new_tail.next
    new_tail.next = None                 # break the ring
    return new_head

for k in (0, 2, 5, 7):
    print(k, show(rotate_right(from_list([1, 2, 3, 4, 5]), k)))
```
```text
0 1 -> 2 -> 3 -> 4 -> 5 -> None
2 4 -> 5 -> 1 -> 2 -> 3 -> None
5 1 -> 2 -> 3 -> 4 -> 5 -> None
7 4 -> 5 -> 1 -> 2 -> 3 -> None
```

`k %= n` is essential: `k` may be larger than the length (here 7 behaves like 2).

### Partition around a value

Rearrange so that all nodes with value `< x` come before the nodes with value `>= x`, keeping the original order inside each group. Use **two dummies**: one list for the small nodes, one for the large ones, then join them.

```python
def partition_list(head, x):
    small_dummy, large_dummy = ListNode(), ListNode()
    small, large = small_dummy, large_dummy
    while head:
        if head.val < x:
            small.next = head
            small = small.next
        else:
            large.next = head
            large = large.next
        head = head.next
    large.next = None                    # IMPORTANT: otherwise the old links can form a cycle
    small.next = large_dummy.next        # join the two parts
    return small_dummy.next

print(show(partition_list(from_list([1, 4, 3, 2, 5, 2]), 3)))
```
```text
1 -> 2 -> 2 -> 4 -> 3 -> 5 -> None
```

The line `large.next = None` is the one people forget. The last "large" node may still point to some node that was moved to the small list, and the result then contains a cycle or repeats nodes.

### Odd and even positions

Group the nodes at odd positions first, then the nodes at even positions (positions, not values): `1 -> 2 -> 3 -> 4 -> 5` becomes `1 -> 3 -> 5 -> 2 -> 4`.

```python
def odd_even_list(head):
    if head is None:
        return None
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next             # link odd nodes together
        odd = odd.next
        even.next = odd.next             # link even nodes together
        even = even.next
    odd.next = even_head                 # the even group goes after the odd group
    return head

print(show(odd_even_list(from_list([1, 2, 3, 4, 5]))))
print(show(odd_even_list(from_list([2, 1, 3, 5, 6, 4, 7]))))
```
```text
1 -> 3 -> 5 -> 2 -> 4 -> None
2 -> 3 -> 6 -> 7 -> 1 -> 5 -> 4 -> None
```

### Remove duplicates from a sorted list

Two versions. **Keep one copy of each value:**

```python
def dedupe_keep_one(head):
    cur = head
    while cur and cur.next:
        if cur.val == cur.next.val:
            cur.next = cur.next.next     # unlink the duplicate; stay on cur
        else:
            cur = cur.next
    return head
```

**Remove every value that occurs more than once** (keep only the values that appear exactly once). Now the head can disappear, so use a dummy.

```python
def dedupe_remove_all(head):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next:
        cur = prev.next
        if cur.next and cur.next.val == cur.val:
            value = cur.val
            while cur and cur.val == value:
                cur = cur.next           # skip the whole run of this value
            prev.next = cur
        else:
            prev = prev.next
    return dummy.next

print(show(dedupe_keep_one(from_list([1, 1, 2, 3, 3, 3]))))
print(show(dedupe_remove_all(from_list([1, 2, 3, 3, 4, 4, 5]))))
print(show(dedupe_remove_all(from_list([1, 1, 1, 2, 3]))))
```
```text
1 -> 2 -> 3 -> None
1 -> 2 -> 5 -> None
2 -> 3 -> None
```

### Add two numbers stored as lists

A number is stored with its digits in **reverse** order (the least significant digit first): `342` is `2 -> 4 -> 3`. Add two such numbers and return the result in the same form. That order is a gift: adding starts from the least significant digit, which is the head.

```python
def add_numbers(a, b):
    dummy = ListNode()
    tail = dummy
    carry = 0
    while a or b or carry:               # carry keeps the loop alive for a final extra digit
        total = carry
        if a:
            total += a.val
            a = a.next
        if b:
            total += b.val
            b = b.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next

print(show(add_numbers(from_list([2, 4, 3]), from_list([5, 6, 4]))))          # 342 + 465 = 807
print(show(add_numbers(from_list([9, 9, 9, 9]), from_list([1]))))             # 9999 + 1 = 10000
print(show(add_numbers(from_list([0]), from_list([0]))))
```
```text
7 -> 0 -> 8 -> None
0 -> 0 -> 0 -> 0 -> 1 -> None
0 -> None
```

### The intersection of two lists

Two lists may *share their tail*: from some node on, both continue with the same nodes (the same objects, not just equal values). Find the first shared node. The trick needs no lengths and no memory: walk two pointers; when one reaches the end, send it to the **head of the other list**. After at most `len(a) + len(b)` steps both have walked the same total distance, so they meet at the shared node (or, if there is none, both become `None` together).

```python
def intersection(head_a, head_b):
    a, b = head_a, head_b
    while a is not b:
        a = a.next if a else head_b
        b = b.next if b else head_a
    return a

shared = from_list([8, 4, 5])
a = from_list([4, 1])
a.next.next = shared                     # a: 4 -> 1 -> 8 -> 4 -> 5
b = from_list([5, 6, 1])
b.next.next.next = shared                # b: 5 -> 6 -> 1 -> 8 -> 4 -> 5
print(intersection(a, b).val, intersection(a, b) is shared)
print(intersection(from_list([1, 2]), from_list([3])))
```
```text
8 True
None
```

If the lists have different lengths, say `x` and `y` nodes before the shared part and `s` shared nodes, then pointer `a` walks `x + s + y` nodes to reach the meeting point through list `b`, and pointer `b` walks `y + s + x`. Equal distances: they arrive together.

### A test for all of them

Each of these has a one-line list version. Compare on random data.

```python
import random

rng = random.Random(33)
ok = True
for _ in range(400):
    a = [rng.randint(0, 5) for _ in range(rng.randint(1, 9))]
    n = rng.randint(1, len(a))
    ok &= to_list(remove_nth_from_end(from_list(a), n)) == a[:len(a) - n] + a[len(a) - n + 1:]
    k = rng.randint(0, 12)
    r = k % len(a)
    ok &= to_list(rotate_right(from_list(a), k)) == (a[-r:] + a[:-r] if r else a)
    x = rng.randint(0, 6)
    ok &= to_list(partition_list(from_list(a), x)) == [v for v in a if v < x] + [v for v in a if v >= x]
    ok &= to_list(odd_even_list(from_list(a))) == a[0::2] + a[1::2]
    ok &= is_palindrome_list(from_list(a)) == (a == a[::-1])
    b = sorted(a)
    ok &= to_list(dedupe_keep_one(from_list(b))) == sorted(set(b))
    ok &= to_list(dedupe_remove_all(from_list(b))) == [v for v in b if b.count(v) == 1]
print("400 random lists: all classics match their list versions:", bool(ok))
```
```text
400 random lists: all classics match their list versions: True
```

The values are small (0 to 5), so there are many duplicates, which is where the dedupe functions and the stable partition could go wrong.

**Try it 7.** Why does `intersection` return `None` for two lists with no shared node, and not loop forever?

<details><summary>Answer</summary>

After pointer `a` finishes list A it jumps to B, and after it finishes B it becomes `None` (the end). Pointer `b` does the same in the other order. Both walk `len(a) + len(b)` nodes and then one more step onto `None`, and at that moment both are `None`, so `a is b` becomes true (`None is None`) and the loop stops. The loop ends because the two pointers **always take the same total number of steps**. If the "jump to the other head" were applied also after the second end, they would cycle forever.

```python
def intersection(head_a, head_b):
    a, b = head_a, head_b
    steps = 0
    while a is not b:
        a = a.next if a else head_b
        b = b.next if b else head_a
        steps += 1
    return a, steps

print(intersection(from_list([1, 2]), from_list([3])))
```
```text
(None, 4)
```

Lengths 2 and 1: each pointer walks the 3 nodes of the two lists and then one more step onto `None`, so it takes 4 steps, and at that moment both are `None`.

</details>

## 10. Copying a list with a random pointer

A harder node: besides `next`, each node has a `random` pointer that may point to **any** node of the list, or to `None`. Make a **deep copy**: a completely new list with the same shape, where no node is shared with the original.

The difficulty: when you create the copy of node A, A's `random` points to a node that may not have a copy yet. The fix uses a dictionary (dsa.04): first create a copy of every node and remember `original -> copy`; then fill in the pointers by looking nodes up.

```python
class RNode:
    def __init__(self, val, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random

def build(pairs):
    """pairs[i] = [value, index of the random target or None]."""
    nodes = [RNode(v) for v, _ in pairs]
    for i, (_, r) in enumerate(pairs):
        if i + 1 < len(nodes):
            nodes[i].next = nodes[i + 1]
        nodes[i].random = nodes[r] if r is not None else None
    return nodes[0] if nodes else None

def serialize(head):
    """[[value, random index or None], ...]  (the shape of the list)."""
    nodes, cur = [], head
    while cur:
        nodes.append(cur)
        cur = cur.next
    index = {id(node): i for i, node in enumerate(nodes)}
    return [[n.val, index[id(n.random)] if n.random else None] for n in nodes]

def copy_random_list(head):
    copy_of = {None: None}               # original node -> its copy (None maps to None)
    cur = head
    while cur:                           # pass 1: a copy of each node, no links yet
        copy_of[cur] = RNode(cur.val)
        cur = cur.next
    cur = head
    while cur:                           # pass 2: set next and random through the dictionary
        copy_of[cur].next = copy_of[cur.next]
        copy_of[cur].random = copy_of[cur.random]
        cur = cur.next
    return copy_of[head]

pairs = [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
original = build(pairs)
copy = copy_random_list(original)
print(serialize(copy))
print(serialize(copy) == serialize(original))

nodes_original, cur = [], original
while cur:
    nodes_original.append(cur); cur = cur.next
nodes_copy, cur = [], copy
while cur:
    nodes_copy.append(cur); cur = cur.next
print("any node shared:", any(a is b for a in nodes_original for b in nodes_copy))
```
```text
[[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
True
any node shared: False
```

Putting `None` into the dictionary (`{None: None}`) is a small trick that removes the `if cur.random` checks: a missing target maps to a missing copy. The method costs `O(n)` time and `O(n)` space. A cleverer method with `O(1)` extra space weaves each copy right after its original (`A -> A' -> B -> B' ...`), sets `A'.random = A.random.next`, and then separates the two lists; it is a good exercise after this one.

## 11. A stack and a queue from linked nodes

You built stacks on lists and queues on `deque` in dsa.08. Here is the same pair on nodes, which shows that both are one-end and two-end versions of the same chain.

**A stack** needs only the head: push and pop at the front, both `O(1)`, with no resizing ever.

**A queue** needs the head (to remove) and the tail (to add), both `O(1)`. This is exactly why we kept a tail pointer in section 3.

```python
class LinkedStack:
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, val):
        self._top = ListNode(val, self._top)         # the new node points at the old top
        self._size += 1

    def pop(self):
        if self._top is None:
            raise IndexError("pop from empty stack")
        node = self._top
        self._top = node.next
        self._size -= 1
        return node.val

    def peek(self):
        if self._top is None:
            raise IndexError("peek at empty stack")
        return self._top.val

    def __len__(self):
        return self._size


class LinkedQueue:
    def __init__(self):
        self._head = None                            # next to leave
        self._tail = None                            # last to arrive
        self._size = 0

    def enqueue(self, val):
        node = ListNode(val)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def dequeue(self):
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        node = self._head
        self._head = node.next
        if self._head is None:                       # the queue became empty: the tail must follow
            self._tail = None
        self._size -= 1
        return node.val

    def __len__(self):
        return self._size


s = LinkedStack()
for x in (1, 2, 3):
    s.push(x)
print(s.pop(), s.peek(), len(s))

q = LinkedQueue()
for x in (1, 2, 3):
    q.enqueue(x)
print(q.dequeue(), q.dequeue(), len(q))
q.dequeue()
q.enqueue(9)                                         # works after the queue was emptied
print(q.dequeue(), len(q))
```
```text
3 2 2
1 2 1
9 0
```

The line `if self._head is None: self._tail = None` is the classic bug location. If the queue becomes empty and the tail still points at the removed node, the next `enqueue` attaches a node to a node that is not in the list, and the new item is lost. The test above (enqueue after emptying) is exactly the case that finds it.

| | `list` as stack | `deque` as queue | Linked stack / queue |
|---|---|---|---|
| Push / pop | `O(1)` amortised | `O(1)` | `O(1)` worst case |
| Memory per item | small | small | a whole node object |
| Speed in practice | very fast | very fast | slower (object creation) |

Use the built-ins in real code. Build linked ones when the exercise asks for them, or when you need a structure whose operations never trigger a big copy.

## 12. The LRU cache

**Cache:** a small, fast store for results that are expensive to compute or fetch (a web page, a database row). It has limited size. When it is full, something must be thrown out. **LRU** (*least recently used*) throws out the item that has not been used for the longest time, on the idea that things used recently will be used again soon.

### The specification

A class `LRUCache(capacity)` with two operations, both required in **`O(1)`**:

- `get(key)`: return the value, or `-1` if absent. A successful `get` makes the key the *most recently used*.
- `put(key, value)`: insert or update; the key becomes the most recently used. If the cache is now over capacity, remove the *least* recently used key.

### Why two structures

- To find a key in `O(1)` we need a **dictionary**.
- To know the usage **order** and to move an item to "most recent" in `O(1)`, we need a **doubly linked list**: removing a node from the middle in `O(1)` needs its `prev`, and a singly linked list cannot do that.

Combine them: the dictionary maps `key -> node`, and the doubly linked list orders the nodes from most recent (next to the head sentinel) to least recent (next to the tail sentinel).

```text
dict:   {1: node1, 2: node2, 3: node3}

head(sentinel) <-> [3] <-> [1] <-> [2] <-> tail(sentinel)
                    ^                 ^
              most recently     least recently
                  used               used
```

Every operation does a dictionary lookup (`O(1)`), then a constant number of pointer changes (`O(1)`).

```python
class CacheNode:
    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.nodes = {}                              # key -> node
        self.head = CacheNode()                      # sentinel: after it comes the most recent
        self.tail = CacheNode()                      # sentinel: before it comes the least recent
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _push_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.nodes:
            return -1
        node = self.nodes[key]
        self._unlink(node)                           # move it to the front: most recent
        self._push_front(node)
        return node.val

    def put(self, key, value):
        if key in self.nodes:
            node = self.nodes[key]
            node.val = value
            self._unlink(node)
            self._push_front(node)
            return
        if len(self.nodes) == self.capacity:
            lru = self.tail.prev                     # the least recently used node
            self._unlink(lru)
            del self.nodes[lru.key]                  # this is why the node stores its key
        node = CacheNode(key, value)
        self.nodes[key] = node
        self._push_front(node)

    def order(self):
        """Keys from most to least recently used (for debugging and tests)."""
        out, cur = [], self.head.next
        while cur is not self.tail:
            out.append(cur.key)
            cur = cur.next
        return out


cache = LRUCache(2)
cache.put(1, 1); print("put 1      ", cache.order())
cache.put(2, 2); print("put 2      ", cache.order())
print("get 1 ->", cache.get(1), cache.order())
cache.put(3, 3); print("put 3 (evicts 2)", cache.order())
print("get 2 ->", cache.get(2))
cache.put(4, 4); print("put 4 (evicts 1)", cache.order())
print("get 1 ->", cache.get(1), "| get 3 ->", cache.get(3), "| get 4 ->", cache.get(4), cache.order())
```
```text
put 1       [1]
put 2       [2, 1]
get 1 -> 1 [1, 2]
put 3 (evicts 2) [3, 1]
get 2 -> -1
put 4 (evicts 1) [4, 3]
get 1 -> -1 | get 3 -> 3 | get 4 -> 4 [4, 3]
```

Follow the trace. After `get 1`, key `1` moves to the front, so key `2` becomes the least recently used. That is why `put 3` throws out `2` and not `1`. Each `get` that hits changes the order.

Three design details worth remembering:

1. **The node stores its key.** When we evict `lru`, we must also delete it from the dictionary, and the only way to know which key it was is to read `lru.key`. Without it, the dictionary would keep a stale entry.
2. **Two sentinels** mean `_unlink` and `_push_front` never test for `None` or for an empty list.
3. **`put` on an existing key** updates the value *and* the position. Forgetting the move makes the cache evict a key that was just written.

### Is it right? Compare with `OrderedDict`

Python's `collections.OrderedDict` remembers insertion order and has `move_to_end`, so a short LRU cache can be built with it. We use that as the trusted model in a differential test.

```python
from collections import OrderedDict
import random

class LRUModel:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)                   # most recent at the end
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)            # drop the least recent (the front)

rng = random.Random(6)
ok = True
for capacity in (1, 2, 3, 5):
    mine, model = LRUCache(capacity), LRUModel(capacity)
    for _ in range(3000):
        key = rng.randint(0, 7)
        if rng.random() < 0.5:
            ok &= mine.get(key) == model.get(key)
        else:
            value = rng.randint(0, 99)
            mine.put(key, value); model.put(key, value)
        ok &= mine.order() == list(reversed(model.data))
print("12000 random operations: the hand-made LRU matches OrderedDict:", bool(ok))
```
```text
12000 random operations: the hand-made LRU matches OrderedDict: True
```

For real programs, caching the result of a *function* is a standard job, and `functools.lru_cache` (core.11) does it with exactly this design inside. Use `OrderedDict` or `lru_cache` in production; build the linked-list version to understand them, and because "implement an LRU cache" is among the most common design questions.

**Predict the output 6.** With capacity 1, what do these calls return?

```python
cache = LRUCache(1)
cache.put(1, 10)
cache.put(2, 20)
print(cache.get(1), cache.get(2))
cache.put(2, 30)
print(cache.get(2), cache.order())
```

<details><summary>Answer</summary>

```text
-1 20
30 [2]
```

Capacity 1: putting key 2 evicts key 1, so `get(1)` is `-1` and `get(2)` is `20`. Then `put(2, 30)` updates the existing key: it is not a new key, so nothing is evicted, and `get(2)` returns the new value `30`. The order has just one key.

</details>

**Try it 8.** In `put`, what goes wrong if you evict *before* checking whether the key is already in the cache, that is, if the capacity check came first and ignored `key in self.nodes`?

<details><summary>Answer</summary>

When the cache is full and you update an existing key, a capacity check that ignores "already present" would evict the least recent item even though the number of entries is not going to grow. You would lose a good entry for nothing. In the code above, the update case returns early, before the capacity check, so a full cache never evicts on an update.

```python
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
cache.put(2, 22)                                     # update: nothing must be evicted
print(cache.get(1), cache.get(2), cache.order())
```
```text
1 22 [2, 1]
```

</details>

## 13. Which technique for which problem?

Most linked-list problems are one of a small number of patterns. Recognise the pattern, and the code follows.

| Clue in the problem | Technique |
|---|---|
| The head may change or be removed | **dummy node** |
| Build a new list node by node | dummy node + `tail` pointer |
| Reverse, or reverse a part, or in groups | `prev` / `cur` / `nxt` (save `nxt` first) |
| "Middle of the list", "split in half" | **slow and fast** pointers |
| "Is there a cycle?", "where does it start?" | slow and fast pointers (Floyd) |
| "The k-th from the end", "remove the n-th from the end" | two pointers with a **gap** |
| Merge sorted lists, sort a list | dummy + merge; merge sort with middle cut |
| Palindrome, reorder | middle + reverse the second half + compare or weave |
| Two lists that may meet | the "switch heads" two-pointer trick |
| Copy nodes that point to other nodes | dictionary `old -> new` |
| Remove a node you hold, in `O(1)` | **doubly** linked list |
| "Most recently used", cache | doubly linked list + dictionary |
| Needs access by index, or binary search | not a linked list: use an array |

A sentence to say to yourself before you code: *"Which links will I change, in which order, and which node variable still holds the part I am about to disconnect?"*

## 14. Linked lists in real Python

The honest picture, with numbers.

### Memory

Every node is a full Python object. A list stores only a reference per item. Let us measure the memory of `100,000` values stored in a list, in a chain of ordinary nodes, and in a chain of nodes with `__slots__` (a class that stores its fields without a per-object dictionary).

```python
import tracemalloc

class PlainNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class SlotNode:
    __slots__ = ("val", "next")
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

N = 100_000

def build_list():
    return list(range(1000, 1000 + N))

def build_chain(cls):
    head = None
    for v in range(1000 + N - 1, 999, -1):
        head = cls(v, head)
    return head

for name, build in (("list", build_list),
                    ("chain of plain nodes", lambda: build_chain(PlainNode)),
                    ("chain of slot nodes", lambda: build_chain(SlotNode))):
    tracemalloc.start()
    keep = build()
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{name:22} about {round(current / N):>3} bytes per item")
```
```text
list                   about  40 bytes per item
chain of plain nodes   about 120 bytes per item
chain of slot nodes    about  80 bytes per item
```

> Machine note: the exact byte counts depend on your Python version and platform. The shape of the result does not: the list needs the least, the plain chain needs about three times as much, and `__slots__` brings a chain to roughly twice a list. Each item of the list is an integer (shared in both cases) plus an 8-byte reference; each node adds an object header and fields.

### Speed

Python's built-in `list` is written in C and keeps its items next to each other in memory, so walking it uses the CPU cache well. A chain is made of separate objects scattered in memory, and each step is a Python-level attribute access.

```python
import time

class Node:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

n = 200_000
data = list(range(n))
head = None
for v in range(n - 1, -1, -1):
    head = Node(v, head)

start = time.perf_counter()
total = 0
for x in data:
    total += x
list_time = time.perf_counter() - start

start = time.perf_counter()
total = 0
cur = head
while cur:
    total += cur.val
    cur = cur.next
chain_time = time.perf_counter() - start

print("walking the chain is slower than looping over the list:", chain_time > list_time)

# inserting at the FRONT, where the chain should win
start = time.perf_counter()
lst = []
for i in range(50_000):
    lst.insert(0, i)
list_front = time.perf_counter() - start

start = time.perf_counter()
front = None
for i in range(50_000):
    front = Node(i, front)
chain_front = time.perf_counter() - start

print("inserting at the front is faster in the chain:", chain_front < list_front)
```
```text
walking the chain is slower than looping over the list: True
inserting at the front is faster in the chain: True
```

Both lines come out as the theory says. The chain wins at the **front** (no shifting), and the list wins at **walking**. A list also has a fast `append` and `pop()` at the back, so for stacks the list is the better choice; for queues use `deque`. In practice you reach for a linked list only when:

- you must remove or insert in the middle **while holding the node** (LRU caches, editors), and
- the number of such operations is large compared with the number of times you walk.

### Where chains hide inside real software

- **`collections.deque`** is a doubly linked list of *blocks*, each holding up to 64 items. This keeps the `O(1)` ends of a chain while fixing most of its memory and speed problems (one node holds many items).
- **Hash tables** that handle collisions by *chaining* keep a small linked list in each bucket.
- **Operating systems** keep free memory blocks and process queues in linked lists.
- **File systems** like FAT store a file as a chain of blocks.
- **Graphs** are often stored as *adjacency lists* (next modules), which are lists of neighbours.
- **Functional languages** build everything from immutable singly linked lists, where adding at the front shares the old list instead of copying it.
- **Undo history**, **browser history** and **playlists** are doubly linked lists.

## 15. Debugging pointer code

Pointer bugs are hard because the program does not crash where the mistake is. It crashes (or loops, or prints a short list) later. Use a method.

1. **Draw it.** Boxes and arrows on paper, with the names of your variables written next to the nodes they point to. Execute your code line by line on the drawing, and update the arrows. Most bugs show up as "oh, this arrow still points to the old node".
2. **Test with 0, 1, 2 and 3 nodes first.** The empty list, the single node and the two-node list break most wrong solutions. Many bugs hide in the head or the tail.
3. **Print with a guard.** Use a `show` that stops after a limit, so a cycle prints `...` instead of hanging.
4. **Count the nodes** before and after an operation that should keep all of them (reverse, sort, partition, reorder).
5. **Compare with a Python list** (a differential test), as in sections 3 and 5.

### A checker for "nothing lost, nothing duplicated"

An operation that only rewires should end with exactly the **same set of node objects** it started with. This helper compares the identities of the nodes before and after, and it cannot loop forever.

```python
def node_ids(head, limit=10_000):
    ids, cur = [], head
    while cur and len(ids) <= limit:
        ids.append(id(cur))
        cur = cur.next
    return ids

def check_same_nodes(head, operation):
    before = node_ids(head)
    new_head = operation(head)
    after = node_ids(new_head)
    ok = sorted(before) == sorted(after) and len(set(after)) == len(after)
    return ok, len(before), len(after)

print("reverse  :", check_same_nodes(from_list(range(6)), reverse_list))
print("sort     :", check_same_nodes(from_list([5, 3, 4, 1]), sort_list))
print("rotate   :", check_same_nodes(from_list(range(6)), lambda h: rotate_right(h, 2)))
print("lost one :", check_same_nodes(from_list(range(6)), lambda h: h.next))
```
```text
reverse  : (True, 6, 6)
sort     : (True, 4, 4)
rotate   : (True, 6, 6)
lost one : (False, 6, 5)
```

The last line is a deliberately bad "operation" that drops the first node: the check reports `False`, and `5` against `6` nodes. The checker would also catch the doubled node of a cycle.

### The symptoms and their causes

| Symptom | Likely cause |
|---|---|
| `AttributeError: 'NoneType' object has no attribute 'next'` | walking past the end; missing `if cur and cur.next`; empty-list case not handled |
| The program never ends | a cycle; a loop that does not advance; forgetting `x.next = None` when cutting a list |
| The result is shorter than expected | a lost link: overwritten before it was saved |
| The result has repeated nodes or a loop | the last node still points to an old node (`tail.next = None` missing) |
| The head is wrong | returning the old `head` instead of `dummy.next` or the new head |
| Works on long lists, fails on one or two nodes | an edge case: empty, single node |

### A cycle made by accident

The most surprising bug: you move nodes into a new list but forget to cut the old link at the end.

```python
head = from_list([1, 2, 3, 4])
second = head.next.next                  # we want to split the list into 1,2 and 3,4
# forgot: head.next.next = None
print(show(head))
print(show(second))
```
```text
1 -> 2 -> 3 -> 4 -> None
3 -> 4 -> None
```

Here nothing is wrong yet, but the two "lists" **share** nodes `3` and `4`, and the first list is not cut. If you now append to the end of the first list, the second list also changes. Whenever you split a list, finish with `last_of_first.next = None`.

**Try it 9.** Write `split_in_half(head)` that returns two lists (the first half and the second half) after cutting the original. For an odd length, the first half gets the extra node. Check it with the "same nodes" idea.

<details><summary>Answer</summary>

```python
def split_in_half(head):
    if head is None or head.next is None:
        return head, None
    slow = fast = head
    while fast.next and fast.next.next:      # slow ends on the FIRST middle
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                         # the cut
    return head, second

first, second = split_in_half(from_list([1, 2, 3, 4, 5]))
print(show(first), "|", show(second))
first, second = split_in_half(from_list([1, 2, 3, 4]))
print(show(first), "|", show(second))
print(split_in_half(None))
```
```text
1 -> 2 -> 3 -> None | 4 -> 5 -> None
1 -> 2 -> None | 3 -> 4 -> None
(None, None)
```

The cut `slow.next = None` is what makes the halves independent. With the first middle, an even list splits into equal halves and an odd list gives the first half one more node.

</details>

## 16. Common traps, collected

1. **Overwriting a link before saving it.** `cur.next = prev` before `nxt = cur.next` loses the rest of the list. Save, then change.
2. **The wrong order of links when inserting.** First point the new node at what follows, then point the previous node at the new node.
3. **Moving `head`.** If you advance the variable `head` while walking, you lose the start. Walk with a separate `cur`.
4. **No empty-list or single-node check.** `head.next.next` on a short list raises `AttributeError`. Test with 0, 1, 2 nodes.
5. **`while cur:` against `while cur.next:`.** The first visits every node; the second stops on the last. Choose by what you need.
6. **Returning the old head.** After reversing, sorting, rotating or deleting the head, the old `head` variable may no longer be the first node. Return the new head (`dummy.next`).
7. **Forgetting `tail.next = None`.** When you build a result from existing nodes (partition, odd-even, reorder, split), the last node may still point to an old node and create a cycle.
8. **Not advancing in a loop that has an `else`.** In `remove_all`, after unlinking a node we must **not** advance `prev`; in the other branch we must. Mixing them skips a node.
9. **Not updating the tail** (or the size) in a class that has them: removing the last node, or emptying the list. A differential test finds it.
10. **A doubly linked list with only one direction fixed.** Every insert and remove changes *four* links (two `next`, two `prev`). Check both directions in tests.
11. **Starting `fast` and `slow` at the same node when you need the first middle.** In merge sort, start `fast = head.next`, or the recursion may never shrink.
12. **Confusing `==` with `is`.** Two different nodes can hold equal values. Compare nodes with `is`, values with `==`.
13. **Using recursion on long lists.** Python's recursion limit (about 1000) makes `reverse_rec` or `merge_rec` fail on long lists. Use loops.
14. **Comparing nodes in a heap.** Push `(value, tie-breaker, node)`, or Python raises `TypeError` on equal values.
15. **Treating a linked list as an array.** Indexing in a loop (`get(head, i)` for each `i`) is `O(n^2)`. Walk once.

## 17. Summary

- A **linked list** is a chain of nodes; each node holds a value and a reference to the next node (`None` ends the chain). You reach the `i`-th item only by walking `i` steps. In exchange, insertion and deletion need only a few link changes.
- A Python variable is a **label**: overwriting a link may lose the nodes behind it. **Save before you overwrite**, and when you insert, link the new node forward *first*.
- Walk with a separate `cur`. Handle the empty and single-node cases. `head` may change, so return the new head.
- A **dummy node** before the head removes every "is this the first node?" special case. It is the standard way to build, delete, merge and partition.
- A class with a **tail** pointer makes `push_back` `O(1)`; `pop_back` is still `O(n)` in a singly linked list. A **doubly linked list** with two **sentinels** makes all end operations and "remove the node I hold" `O(1)`, at the cost of four links per change.
- **Reversal:** `nxt = cur.next; cur.next = prev; prev = cur; cur = nxt`. The same loop reverses a sub-list or groups of `k`.
- **Fast and slow pointers** find the middle and detect a cycle (Floyd) in `O(1)` space. Reset one pointer to the head to find the start of the cycle. The idea also works on arrays and number sequences (duplicate finding, happy numbers).
- **Merging** two sorted lists takes `O(n + m)` time and `O(1)` space; `k` lists take `O(N log k)` with a heap or pairwise merging; **merge sort** sorts a list in `O(n log n)`.
- Palindrome, reorder, rotate, partition, remove the n-th from the end and intersection are combinations of these tools.
- A stack and a queue can be built from nodes with all operations `O(1)`. An **LRU cache** is a dictionary plus a doubly linked list.
- In real Python, a `list` is faster and smaller. Use chains to learn pointers, to pass interviews, and when you must unlink a node you already hold. Test pointer code by drawing it, trying 0, 1, 2 nodes, checking that no node is lost, and comparing with a Python list.

### Self-check

- [ ] I can write a `ListNode` and the helpers `from_list`, `to_list`, `show` from memory.
- [ ] I can implement push, pop, insert and remove in a singly linked list, and keep head, tail and size right.
- [ ] I can explain why a dummy node removes special cases, and use one to delete nodes and to build a list.
- [ ] I can write a doubly linked list with sentinels and explain the order of the four link changes.
- [ ] I can reverse a list iteratively, recursively, between two positions, and in groups of `k`.
- [ ] I can find the middle, detect a cycle, find its start, and explain why the two pointers must meet.
- [ ] I can merge two sorted lists, merge `k` lists, and sort a list with merge sort.
- [ ] I can solve palindrome, reorder, rotate, partition and remove-n-th-from-end without looking.
- [ ] I can build an LRU cache and explain why it needs both a dictionary and a doubly linked list.
- [ ] I can test pointer code with 0, 1, 2 nodes, a node-conservation check and a differential test.

### How to practise

Do the problems in the order of the chapter: node and list basics first (walk, count, find), then insert and delete (use a dummy), then reversal in all its forms, then fast and slow pointers, then merging and sorting, then the rearrangements, and last the data-structure designs (stack, queue, doubly linked list, LRU cache). **Draw every problem on paper before coding it.** Always test with an empty list, a single node and two nodes. For every function that rewires nodes, ask: *which links change, in which order, and what still holds the part I disconnect?* The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list.

### Further reading

- Robert Sedgewick and Kevin Wayne, *Algorithms*, section 1.3 ("Bags, Queues, and Stacks") for linked-list implementations of stacks and queues.
- Donald Knuth, *The Art of Computer Programming*, volume 1, section 2.2 ("Linear Lists") and section 2.2.3 ("Linked Allocation").
- Linus Torvalds' remarks on "good taste" in code: his example is deleting a node from a linked list with a pointer to a pointer, which removes the special case for the head without a dummy node.
- The Python documentation of `collections.deque`, `collections.OrderedDict` and `functools.lru_cache`.
- Floyd's cycle-finding algorithm in the Wikipedia article "Cycle detection", with the proof and the Brent variant.

Next module: **dsa.10 Trees**.
