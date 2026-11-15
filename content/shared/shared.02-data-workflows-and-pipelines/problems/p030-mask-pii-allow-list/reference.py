def mask_email(email):
    if email is None:
        return None
    local, at, domain = email.strip().lower().rpartition("@")
    if not at or not local or not domain:
        return "***"
    return f"{local[0]}***@{domain}"


def select_columns(row, allowed):
    return {name: row[name] for name in allowed if name in row}


def prepare_export(rows, allowed):
    out = []
    for row in rows:
        kept = select_columns(row, allowed)
        if "email" in kept:
            kept["email"] = mask_email(kept["email"])
        out.append(kept)
    return out
