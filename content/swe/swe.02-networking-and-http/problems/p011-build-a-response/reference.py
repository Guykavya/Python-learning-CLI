from http import HTTPStatus


def build_response(status, body="", content_type="text/plain; charset=utf-8"):
    try:
        phrase = HTTPStatus(status).phrase
    except ValueError:
        phrase = "Unknown"
    if isinstance(body, str):
        body = body.encode("utf-8")
    lines = [f"HTTP/1.1 {status} {phrase}"]
    if status in (204, 304) or 100 <= status < 200:
        if body:
            raise ValueError(f"a {status} response has no body")
        return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")
    lines.append(f"Content-Type: {content_type}")
    lines.append(f"Content-Length: {len(body)}")
    return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1") + body
