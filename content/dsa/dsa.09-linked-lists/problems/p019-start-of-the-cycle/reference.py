class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def detect_cycle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:                 # phase 1: they met inside the cycle
            p = head
            while p is not slow:         # phase 2: both move one step at a time
                p = p.next
                slow = slow.next
            return p                     # the first node of the cycle
    return None
