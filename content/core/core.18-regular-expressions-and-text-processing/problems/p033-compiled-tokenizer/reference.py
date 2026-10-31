import re

TOKEN_SPEC = [
    ("NUMBER", r"\d+(?:\.\d+)?"),
    ("NAME", r"[A-Za-z_]\w*"),
    ("OP", r"[-+*/=()]"),
    ("SKIP", r"\s+"),
    ("MISMATCH", r"."),
]


class Tokenizer:
    def __init__(self):
        master = "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC)
        self.pattern = re.compile(master)

    def tokens(self, text):
        for m in self.pattern.finditer(text):
            kind = m.lastgroup
            value = m.group()
            if kind == "SKIP":
                continue
            if kind == "MISMATCH":
                raise ValueError(f"unexpected character {value!r} at index {m.start()}")
            yield (kind, value)
