import re

FIELD = re.compile(
    r"""
    (?: ^ | , )                 # a field starts at the beginning or after a comma
    \s*
    (?:
        "(?P<quoted>(?:[^"]|"")*)"    # quoted: anything but a quote, or a doubled quote
      | (?P<plain>[^,"]*?)            # unquoted: as little as possible, no comma
    )
    \s*
    (?= , | $ )                 # and it ends right before a comma or the end
    """,
    re.VERBOSE,
)


def split_fields(line: str) -> list[str]:
    fields = []
    for m in FIELD.finditer(line):
        if m.group("quoted") is not None:
            fields.append(m.group("quoted").replace('""', '"'))
        else:
            fields.append(m.group("plain"))
    return fields
