from bisect import bisect_left, bisect_right


def grade(score: int, breakpoints: list[int] = [60, 70, 80, 90], grades: str = "FDCBA") -> str:
    return grades[bisect_right(breakpoints, score)]


def count_in_range(sorted_nums: list[int], lo: int, hi: int) -> int:
    if lo > hi:
        return 0
    return bisect_right(sorted_nums, hi) - bisect_left(sorted_nums, lo)
