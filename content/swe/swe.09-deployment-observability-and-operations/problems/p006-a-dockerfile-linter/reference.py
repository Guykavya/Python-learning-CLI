import shlex

RISKY_WORDS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "PRIVATE_KEY")


def _instructions(text):
    """Yield (first line number, KEYWORD, rest of the instruction), with backslash continuations joined."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        number, line = i + 1, lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        while line.endswith("\\") and i < len(lines):
            line = line[:-1].rstrip() + " " + lines[i].strip()
            i += 1
        keyword, _, rest = line.partition(" ")
        yield number, keyword.upper(), rest.strip()


def _is_risky(name):
    name = name.upper()
    return any(word in name for word in RISKY_WORDS) or name.endswith("_KEY")


def _pairs(keyword, rest):
    try:
        tokens = shlex.split(rest)
    except ValueError:
        tokens = rest.split()
    if keyword == "ARG":
        return [tuple(token.split("=", 1)) for token in tokens if "=" in token]
    if tokens and all("=" in token for token in tokens):
        return [tuple(token.split("=", 1)) for token in tokens]
    if tokens:
        return [(tokens[0], " ".join(tokens[1:]))]                 # the old form: ENV NAME value
    return []


def lint_dockerfile(text):
    findings, stages = [], set()
    first_install = None
    copy_all_lines = []
    last_user = None
    for number, keyword, rest in _instructions(text):
        if keyword == "FROM":
            tokens = [t for t in rest.split() if not t.startswith("--")]
            image = tokens[0] if tokens else ""
            if len(tokens) >= 3 and tokens[1].lower() == "as":
                alias = tokens[2].lower()
            else:
                alias = None
            skip = image.lower() in stages or image == "scratch" or "$" in image or "@sha256:" in image
            if not skip:
                name = image.rsplit("/", 1)[-1]
                if ":" not in name or name.split(":", 1)[1] == "latest":
                    findings.append((number, "unpinned-base"))
            if alias:
                stages.add(alias)
            last_user = None                                        # only the last stage matters for USER
        elif keyword in ("CMD", "ENTRYPOINT"):
            if not rest.startswith("["):
                findings.append((number, "shell-cmd"))
        elif keyword in ("COPY", "ADD"):
            tokens = [t for t in rest.split() if not t.startswith("--")]
            sources = tokens[:-1]
            if any(source in (".", "./") for source in sources) and "--from=" not in rest:
                copy_all_lines.append(number)
        elif keyword == "RUN":
            if "pip install" in rest and first_install is None:
                first_install = number
            if ("apt-get install" in rest or "apt install" in rest) and "rm -rf /var/lib/apt/lists" not in rest:
                findings.append((number, "apt-no-cleanup"))
        elif keyword == "USER":
            last_user = rest.split()[0] if rest.split() else None
        elif keyword in ("ENV", "ARG"):
            for name, value in _pairs(keyword, rest):
                if _is_risky(name) and value and not value.startswith("$"):
                    findings.append((number, "secret-in-env"))
                    break
    if first_install is not None:
        findings += [(n, "copy-before-install") for n in copy_all_lines if n < first_install]
    if last_user is None or last_user.split(":")[0] in ("root", "0"):
        findings.append((0, "no-user"))
    return sorted(set(findings))
