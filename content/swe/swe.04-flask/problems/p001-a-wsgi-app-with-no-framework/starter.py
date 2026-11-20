def app(environ, start_response):
    # TODO: look at environ["PATH_INFO"] and environ["QUERY_STRING"]
    start_response("200 OK", [("Content-Type", "text/plain")])
    return ["Hello"]
