import json
from typing import NotRequired, TypedDict


class Address(TypedDict):
    city: str
    zip: str


class User(TypedDict):
    id: int
    name: str
    address: Address
    tags: NotRequired[list[str]]
    nickname: NotRequired[str | None]


def check_value(value, tp):
    # TODO: int, float, str, bool, list[X], unions, None, nested TypedDict
    return True


def validate(data, td):
    # TODO: TypeError / ValueError as described; return data when valid
    return data


def load_user(text):
    # TODO: json.loads, then validate against User
    return json.loads(text)
