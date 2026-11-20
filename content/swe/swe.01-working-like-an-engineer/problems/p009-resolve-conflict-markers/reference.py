def _is_start(line):
    return line.startswith("<<<<<<<") and (len(line) == 7 or line[7] == " ")


def _is_end(line):
    return line.startswith(">>>>>>>") and (len(line) == 7 or line[7] == " ")


def resolve(text, choose):
    if not callable(choose) and choose not in ("ours", "theirs", "both"):
        raise ValueError(f"choose must be 'ours', 'theirs', 'both' or a function, not {choose!r}")
    out = []
    state = 0          # 0 outside, 1 in our part, 2 in their part
    start = 0
    ours = []
    theirs = []
    for n, line in enumerate(text.split("\n"), 1):
        if state == 0:
            if _is_start(line):
                state, start, ours, theirs = 1, n, [], []
            elif _is_end(line):
                raise ValueError(f"line {n}: '>>>>>>>' without a matching '<<<<<<<'")
            else:
                out.append(line)
        else:
            if _is_start(line):
                raise ValueError(f"line {n}: a second '<<<<<<<' inside the block that began at line {start}")
            if line == "=======":
                if state == 2:
                    raise ValueError(f"line {n}: a second '=======' in the block that began at line {start}")
                state = 2
            elif _is_end(line):
                if state == 1:
                    raise ValueError(f"line {n}: '>>>>>>>' before '=======' in the block that began at line {start}")
                if callable(choose):
                    out.extend(choose(list(ours), list(theirs)))
                elif choose == "ours":
                    out.extend(ours)
                elif choose == "theirs":
                    out.extend(theirs)
                else:
                    out.extend(ours + theirs)
                state = 0
            elif state == 1:
                ours.append(line)
            else:
                theirs.append(line)
    if state != 0:
        raise ValueError(f"line {start}: the conflict block that begins here is never closed")
    return "\n".join(out)
