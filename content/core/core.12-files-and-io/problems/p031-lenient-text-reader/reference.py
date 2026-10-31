def read_text_lenient(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(), False
    except UnicodeDecodeError:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(), True
