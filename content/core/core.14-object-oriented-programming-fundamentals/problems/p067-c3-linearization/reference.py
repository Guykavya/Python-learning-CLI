def _merge(lists):
    lists = [list(seq) for seq in lists if seq]
    result = []
    while lists:
        for seq in lists:
            head = seq[0]
            if not any(head in other[1:] for other in lists):
                break
        else:
            stuck = []
            for seq in lists:
                if seq[0] not in stuck:
                    stuck.append(seq[0])
            names = ", ".join(stuck)
            raise TypeError(f"Cannot create a consistent method resolution order (MRO) for bases {names}")
        result.append(head)
        for seq in lists:
            if seq[0] == head:
                del seq[0]
        lists = [seq for seq in lists if seq]
    return result


def mro(cls_name, bases_map):
    if cls_name == "object":
        return ["object"]
    bases = list(bases_map[cls_name]) or ["object"]
    for i, base in enumerate(bases):
        if base in bases[:i]:
            raise TypeError(f"duplicate base class {base}")
    parent_mros = [mro(base, bases_map) for base in bases]
    return [cls_name] + _merge(parent_mros + [bases])
