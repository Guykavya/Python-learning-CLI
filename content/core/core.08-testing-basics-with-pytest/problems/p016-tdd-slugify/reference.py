def slugify(text):
    """Turn a title into a lower-case, hyphen-separated slug."""
    words = []
    for word in text.lower().split():
        kept = ""
        for ch in word:
            if ch.isalnum():
                kept += ch
        if kept != "":
            words.append(kept)
    return "-".join(words)
