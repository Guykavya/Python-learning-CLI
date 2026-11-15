class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def remove_all(head, target):
    dummy = ListNode(0, head)
    # TODO: walk with prev; unlink prev.next when it matches
    return head
