def get_port(config):
    """Port from config (a dict); the value may be a string. Default 8080."""
    if "port" in config:
        return int(config["port"])
    else:
        return 8080


def add_word(index, word, line_no):
    """index maps word -> list of line numbers. Add line_no under word."""
    if word not in index:
        index[word] = []
    index[word].append(line_no)


def read_or_default(fs, path, default=""):
    """Text of the file, or default if the file does not exist."""
    if fs.exists(path):
        with fs.open(path) as f:
            return f.read()
    else:
        return default


def display_name(obj):
    """obj.name in capitals, or 'ANON' if obj has no name."""
    if hasattr(obj, "name"):
        return obj.name.upper()
    return "ANON"


def parse_int(text):
    """int(text), or None if text is not a whole number."""
    if text.isdigit():
        return int(text)
    return None
