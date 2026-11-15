class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    # TODO: fast n ahead, then both together until fast is on the last node; unlink after slow
    return head
