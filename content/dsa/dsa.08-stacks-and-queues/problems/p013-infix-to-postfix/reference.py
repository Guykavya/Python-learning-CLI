PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def to_postfix(tokens):
    out, ops = [], []
    for t in tokens:
        if t.isdigit():
            out.append(t)
        elif t in PREC:
            while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[t]:
                out.append(ops.pop())
            ops.append(t)
        elif t == "(":
            ops.append(t)
        else:
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()
    while ops:
        out.append(ops.pop())
    return out
