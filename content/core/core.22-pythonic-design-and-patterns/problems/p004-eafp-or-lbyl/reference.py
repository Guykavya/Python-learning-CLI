def get_port(config):
    return int(config.get("port", 8080))


def add_word(index, word, line_no):
    index.setdefault(word, []).append(line_no)


def read_or_default(fs, path, default=""):
    try:
        with fs.open(path) as f:
            return f.read()
    except FileNotFoundError:
        return default


def display_name(obj):
    name = getattr(obj, "name", None)
    return "ANON" if name is None else name.upper()


def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None
