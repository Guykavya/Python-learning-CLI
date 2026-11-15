class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def rotate_right(head, k):
    if head is None or head.next is None:
        return head
    n = 1
    tail = head
    while tail.next is not None:         # length and last node in one walk
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    new_tail = head
    for _ in range(n - k - 1):           # the node before the new head
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    tail.next = head
    return new_head
