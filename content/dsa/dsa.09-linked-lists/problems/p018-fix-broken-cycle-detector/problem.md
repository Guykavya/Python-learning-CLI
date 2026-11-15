# Fix the broken cycle detector

`starter.py` holds a cycle detector written by a classmate. Their idea: "if the fast pointer comes back to the **head**, we went round a cycle."

```python
def has_cycle(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if fast is head:             # "the hare is back at the start: we went round"
            return True
    return False
```

It passes their tests:

```text
1 -> 2 -> 3 -> None              False   (correct)
1 -> 2 -> 3 -> back to 1         True    (correct)
```

But on this list it **never returns**: the program hangs.

```text
1 -> 2 -> 3
     ^    |
     +----+          (3.next is 2: a 2-node cycle that does not include the head)
```

1. Trace `slow` and `fast` on that list for five rounds. Why is `fast is head` never true?
2. Which comparison guarantees that the loop stops on **every** list with a cycle? Fix the function with the smallest change.
3. Keep `O(1)` memory: no set or list of nodes. Do not change the list.

## Example

After the fix:

```python
>>> has_cycle(list_1_2_3_with_3_pointing_to_2)
True
>>> has_cycle(list_1_2_3_ending_in_None)
False
```

The tests run every case in a separate process with a time limit, so a detector that loops forever fails with a message instead of hanging.

## Think about

A cycle can start anywhere. Which nodes does `fast` visit forever once it is inside a cycle that does not contain the head?
