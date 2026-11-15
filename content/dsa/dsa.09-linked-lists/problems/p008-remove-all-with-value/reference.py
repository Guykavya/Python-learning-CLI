class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def remove_all(head, target):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next is not None:
        if prev.next.val == target:
            prev.next = prev.next.next      # unlink; do NOT move prev
        else:
            prev = prev.next
    return dummy.next
