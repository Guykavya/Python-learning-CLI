class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy                       # the node before the current group
    while True:
        kth = group_prev                     # find the k-th node of the group
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next            # fewer than k nodes left: keep them
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:         # reverse the group, its end points at group_next
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        first = group_prev.next              # the old first node is now the group's last
        group_prev.next = kth
        group_prev = first
