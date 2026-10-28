def count_stats(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return (len(text.splitlines()), len(text.split()), len(text))
