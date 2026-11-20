import heapq


def huffman_tree(freq):
    heap = []
    tie = 0
    for letter in sorted(freq):
        heap.append((freq[letter], tie, letter))
        tie += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        w1, _, t1 = heapq.heappop(heap)
        w2, _, t2 = heapq.heappop(heap)
        heapq.heappush(heap, (w1 + w2, tie, (t1, t2)))
        tie += 1
    return heap[0][2]


def code_lengths(freq):
    if len(freq) == 1:
        return {next(iter(freq)): 1}           # a lone letter still needs one bit
    lengths = {}
    stack = [(huffman_tree(freq), 0)]          # (subtree, depth); no recursion needed
    while stack:
        tree, depth = stack.pop()
        if isinstance(tree, str):
            lengths[tree] = depth
        else:
            stack.append((tree[0], depth + 1))
            stack.append((tree[1], depth + 1))
    return lengths


def total_bits(freq):
    lengths = code_lengths(freq)
    return sum(freq[x] * lengths[x] for x in freq)
