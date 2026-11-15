class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def cycle_length(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:                 # inside the cycle: walk once round it
            length = 1
            cur = slow.next
            while cur is not slow:
                cur = cur.next
                length += 1
            return length
    return 0
