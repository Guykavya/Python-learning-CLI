def convert_record(record, schema):
    """Return a new dict with each schema field converted; raise ValueError naming the field."""
    result = {}
    for field, converter in schema.items():
        if field not in record:
            raise ValueError(f"missing field {field!r}")
        value = record[field]
        try:
            result[field] = converter(value)
        except ValueError as e:
            raise ValueError(f"field {field!r}: could not convert {value!r} with {converter.__name__}") from e
    return result
