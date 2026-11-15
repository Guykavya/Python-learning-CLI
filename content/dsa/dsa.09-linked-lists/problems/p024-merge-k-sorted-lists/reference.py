class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


import heapq


def merge_k(lists):
    heap = []
    for i, node in enumerate(lists):
        if node is not None:
            heap.append((node.val, i, node))     # i breaks ties: nodes are never compared
    heapq.heapify(heap)
    dummy = ListNode()
    tail = dummy
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, i, node.next))
    tail.next = None
    return dummy.next
