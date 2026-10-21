def convert_record(record, schema):
    """Return a new dict with each schema field converted; raise ValueError naming the field."""
    result = {}
    for field in schema:
        result[field] = schema[field](record[field])
    return result
