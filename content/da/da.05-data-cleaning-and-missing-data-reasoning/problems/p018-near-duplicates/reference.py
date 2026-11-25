from difflib import SequenceMatcher


def _normalise(name):
    return " ".join(name.lower().split())


def similar_names(names, threshold=0.85):
    """Pairs (i, j), i < j, of names whose similarity ratio is at least `threshold`."""
    keys = [_normalise(n) for n in names]
    pairs = []
    matcher = SequenceMatcher(None)
    for j in range(len(keys)):
        matcher.set_seq2(keys[j])
        for i in range(j):
            matcher.set_seq1(keys[i])
            # the two quick ratios are cheap upper bounds of ratio(): skip hopeless pairs
            if (matcher.real_quick_ratio() >= threshold and matcher.quick_ratio() >= threshold
                    and matcher.ratio() >= threshold):
                pairs.append((i, j))
    return sorted(pairs)
