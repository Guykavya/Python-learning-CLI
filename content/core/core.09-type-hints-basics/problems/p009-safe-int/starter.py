def safe_int(text):
    return int(text.strip())


def safe_int_or(text, default):
    return int(text.strip())


def parse_all(texts):
    return [int(t) for t in texts]
