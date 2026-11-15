class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def has_cycle(head):
    slow = fast = head
    # TODO: move slow by one and fast by two; meeting means a cycle, fast reaching the end means none
    return None
