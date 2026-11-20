from urllib.parse import parse_qs


def app(environ, start_response):
    if environ["PATH_INFO"] == "/hello":
        query = parse_qs(environ.get("QUERY_STRING", ""))
        name = query.get("name", ["world"])[0]
        status, text = "200 OK", f"Hello, {name}"
    else:
        status, text = "404 Not Found", "Not Found"
    body = text.encode("utf-8")
    start_response(status, [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ])
    return [body]
