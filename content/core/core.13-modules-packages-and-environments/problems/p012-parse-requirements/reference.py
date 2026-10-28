def normalise_name(name):
    return name.lower().replace("_", "-").replace(".", "-")


def parse_requirements(path):
    result = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.partition("#")[0].strip()
            if not line or line.startswith("-"):
                continue
            line = line.partition(";")[0].strip()
            i = 0
            while i < len(line) and (line[i].isalnum() or line[i] in "-_."):
                i += 1
            name = normalise_name(line[:i])
            rest = line[i:].strip()
            if rest.startswith("["):
                rest = rest.partition("]")[2]
            spec = rest.replace(" ", "").replace("\t", "")
            result.append((name, spec))
    return result
