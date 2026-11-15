class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def add_two_numbers(a, b):
    dummy = ListNode()
    tail = dummy
    carry = 0
    while a is not None or b is not None or carry:
        total = carry
        if a is not None:
            total += a.val
            a = a.next
        if b is not None:
            total += b.val
            b = b.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next
