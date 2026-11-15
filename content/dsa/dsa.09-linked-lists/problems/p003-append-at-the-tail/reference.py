class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def append(head, val):
    node = ListNode(val)
    if head is None:
        return node
    cur = head
    while cur.next is not None:     # stop ON the last node
        cur = cur.next
    cur.next = node
    return head
