from collections import defaultdict


def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        if word:
            groups[word[0].lower()].append(word)
    return dict(groups)


def count_by_length(words: list[str]) -> dict[int, int]:
    counts: defaultdict[int, int] = defaultdict(int)
    for word in words:
        counts[len(word)] += 1
    return dict(counts)
