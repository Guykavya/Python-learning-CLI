class RNode:
    def __init__(self, val, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random


def copy_random_list(head):
    # TODO: deep copy; no shared nodes; randoms point into the copy; the original stays unchanged
    return head
