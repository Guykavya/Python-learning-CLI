def mangle(class_name, attr):
    for text in (class_name, attr):
        if not text.isidentifier():
            raise ValueError(f"not an identifier: {text!r}")
    if not attr.startswith("__") or attr.endswith("__"):
        return attr
    stripped = class_name.lstrip("_")
    if stripped == "":
        return attr
    return "_" + stripped + attr
