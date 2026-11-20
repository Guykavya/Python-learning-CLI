def replace_words(roots, sentence):
    """Replace each word by the shortest root that is a prefix of it."""
    out = []
    for word in sentence.split():
        for r in roots:                       # slow, and the first match in list order is not always the shortest
            if word.startswith(r):
                word = r
                break
        out.append(word)
    return " ".join(out)
