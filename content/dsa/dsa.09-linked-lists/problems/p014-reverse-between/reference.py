class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next                 # the node just before position left
    first = before.next                      # becomes the last node of the reversed part
    prev, cur = None, first
    for _ in range(right - left + 1):
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    before.next = prev                       # connect the front to the reversed part
    first.next = cur                         # connect the reversed part to the rest
    return dummy.next
