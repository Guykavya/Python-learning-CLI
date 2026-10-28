from typing import TypeGuard


def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)


def is_int_dict(value: dict[str, object]) -> TypeGuard[dict[str, int]]:
    return all(isinstance(v, int) and not isinstance(v, bool) for v in value.values())


def join_if_strings(items: list[object]) -> str:
    if is_str_list(items):
        return ", ".join(items)
    return ""


def sum_counts(data: dict[str, object]) -> int:
    if is_int_dict(data):
        return sum(data.values())
    raise ValueError("every value must be an int")
