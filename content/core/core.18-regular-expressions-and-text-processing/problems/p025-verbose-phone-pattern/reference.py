import re

PHONE_RE = re.compile(r"""
    (?:\+1[ -]?)?                    # optional country code: +1, then a space or hyphen
    (?P<area>                        # area code, first digit 2-9 ...
        \([2-9]\d{2}\)               #   ... in brackets: (555)
      | [2-9]\d{2}                   #   ... or bare: 555
    )
    [-. ]?                           # optional separator (a space inside [] is kept)
    (?P<exchange>\d{3})              # exchange
    [-. ]?                           # optional separator
    (?P<line>\d{4})                  # line number
    (?:                              # optional extension
        \s*(?:ext\.?|x)\s*           #   'ext', 'ext.' or 'x'
        (?P<ext>\d{1,5})             #   1 to 5 digits
    )?
""", re.VERBOSE)


def parse_phone(s: str) -> dict | None:
    m = PHONE_RE.fullmatch(s.strip())
    if m is None:
        return None
    result = m.groupdict()
    result["area"] = result["area"].strip("()")
    return result
