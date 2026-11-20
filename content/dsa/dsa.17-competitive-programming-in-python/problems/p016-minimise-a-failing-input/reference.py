def shrink(case, fails):
    case = list(case)
    if not fails(case):
        raise ValueError("the case does not fail")
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(case):
            candidate = case[:i] + case[i + 1:]
            if fails(candidate):
                case = candidate
                changed = True
            else:
                i += 1
    return case
