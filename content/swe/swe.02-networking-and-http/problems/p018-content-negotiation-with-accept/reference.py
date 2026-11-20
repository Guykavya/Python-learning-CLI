def _parse(accept):
    ranges = []
    for part in accept.split(","):
        pieces = [p.strip() for p in part.split(";")]
        media = pieces[0].lower()
        if "/" not in media:
            continue
        q = 1.0
        for param in pieces[1:]:
            name, _, value = param.partition("=")
            if name.strip().lower() == "q":
                try:
                    q = float(value)
                except ValueError:
                    q = 0.0
        ranges.append((media, q))
    return ranges


def _specificity(media_range, offered):
    if media_range == offered:
        return 3
    if media_range.endswith("/*") and media_range[:-1] == offered.split("/")[0] + "/":
        return 2
    if media_range == "*/*":
        return 1
    return 0


def choose(accept_header, offered):
    if not offered:
        return None
    if accept_header is None or not accept_header.strip():
        return offered[0]
    ranges = _parse(accept_header)
    best, best_q = None, 0.0
    for candidate in offered:
        found = (0, 0.0)
        for media, q in ranges:
            spec = _specificity(media, candidate.lower())
            if spec > found[0]:
                found = (spec, q)
        q = found[1]
        if q > best_q:
            best, best_q = candidate, q
    return best
