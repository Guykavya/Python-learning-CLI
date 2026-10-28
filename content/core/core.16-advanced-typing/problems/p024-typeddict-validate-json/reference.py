import json
import types
from typing import (
    Any,
    NotRequired,
    TypedDict,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)


class Address(TypedDict):
    city: str
    zip: str


class User(TypedDict):
    id: int
    name: str
    address: Address
    tags: NotRequired[list[str]]
    nickname: NotRequired[str | None]


def check_value(value: object, tp: Any) -> bool:
    if tp is None or tp is type(None):
        return value is None
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        return any(check_value(value, member) for member in get_args(tp))
    if origin is list:
        (item_type,) = get_args(tp)
        return isinstance(value, list) and all(check_value(v, item_type) for v in value)
    if is_typeddict(tp):
        try:
            validate(value, tp)
        except (TypeError, ValueError):
            return False
        return True
    if tp is bool:
        return isinstance(value, bool)
    if tp is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if tp is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, tp)


def validate(data: object, td: Any) -> Any:
    if not isinstance(data, dict):
        raise TypeError(f"expected a dict for {td.__name__}, got {type(data).__name__}")
    hints = get_type_hints(td)
    for key in td.__required_keys__:
        if key not in data:
            raise ValueError(f"missing required key {key!r}")
    for key, value in data.items():
        if key not in hints:
            raise ValueError(f"unexpected key {key!r}")
        if not check_value(value, hints[key]):
            raise TypeError(f"key {key!r} has the wrong type: {type(value).__name__}")
    return data


def load_user(text: str) -> User:
    return validate(json.loads(text), User)  # type: ignore[no-any-return]
