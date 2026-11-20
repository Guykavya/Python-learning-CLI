class ApiError(Exception):
    def __init__(self, status, code, message):
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def raise_for_api(response):
    # TODO: return the response for status < 400; otherwise find code and message (JSON or fallback) and raise ApiError
    return response
