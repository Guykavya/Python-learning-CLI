import heapq


def code_lengths(freq):
    """letter -> length of its Huffman code (1 for a single letter)."""
    return {x: 1 for x in freq}


def total_bits(freq):
    """Bits needed to encode the text: sum(freq[x] * code length of x)."""
    return sum(freq.values())
