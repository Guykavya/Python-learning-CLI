class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):                   # fast goes n nodes ahead
        fast = fast.next
    while fast.next is not None:         # keep the gap until fast is on the last node
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next           # slow is just before the node to remove
    return dummy.next
