PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def to_postfix(tokens):
    out, ops = [], []
    for t in tokens:
        if t.isdigit():
            out.append(t)
        # TODO: operators, "(" and ")"
    return out
