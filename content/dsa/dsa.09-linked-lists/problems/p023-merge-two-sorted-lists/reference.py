class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_two(a, b):
    dummy = ListNode()
    tail = dummy
    while a is not None and b is not None:
        if b.val < a.val:                # strictly smaller: on a tie, a goes first (stable)
            tail.next = b
            b = b.next
        else:
            tail.next = a
            a = a.next
        tail = tail.next
    tail.next = a if a is not None else b    # one list is used up: link the rest of the other
    return dummy.next
