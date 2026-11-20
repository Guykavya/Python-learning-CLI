import base64
import json


def encode_cursor(created: int, row_id: int) -> str:
    raise NotImplementedError("write encode_cursor()")


def decode_cursor(cursor: str):
    raise NotImplementedError("write decode_cursor()")


def page_after(rows, cursor=None, limit=3):
    raise NotImplementedError("write page_after()")
