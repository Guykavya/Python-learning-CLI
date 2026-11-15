PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
         "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def letter_combinations(digits):
    if not digits:
        return []
    result, path = [], []

    def go(i):
        if i == len(digits):
            result.append("".join(path))
            return
        for ch in PHONE[digits[i]]:
            path.append(ch)
            go(i + 1)
            path.pop()

    go(0)
    return result
