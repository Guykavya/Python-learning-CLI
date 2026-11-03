def type_ok(value, expected):
    """isinstance, except that bool only counts as bool, and int counts as float."""
    if isinstance(value, bool):
        return expected is bool
    if expected is float:
        return isinstance(value, (int, float))
    return isinstance(value, expected)


def check_schema(record, schema):
    """Return a list of error strings; [] means the record matches the schema."""
    errors = []
    for field, rule in schema.items():
        if field not in record:
            if rule["required"]:
                errors.append(f"{field}: missing")
            continue
        value = record[field]
        if value is None:
            if rule["required"]:
                errors.append(f"{field}: null")
            continue
        if not type_ok(value, rule["type"]):
            errors.append(f"{field}: expected {rule['type'].__name__}, got {type(value).__name__}")
    for field in record:
        if field not in schema:
            errors.append(f"{field}: unexpected field")
    return errors
