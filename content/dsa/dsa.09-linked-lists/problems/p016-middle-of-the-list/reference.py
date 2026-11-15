class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def middle_node(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next             # one step
        fast = fast.next.next        # two steps
    return slow
