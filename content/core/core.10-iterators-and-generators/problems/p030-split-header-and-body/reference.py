from itertools import takewhile


def split_message(lines):
    it = iter(lines)
    headers = {}
    for line in takewhile(lambda line: line.strip() != "", it):
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    body = list(it)
    return headers, body
