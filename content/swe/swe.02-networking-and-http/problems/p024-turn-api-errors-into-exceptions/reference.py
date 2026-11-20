from http import HTTPStatus

CODES = {400: "bad-request", 401: "unauthorized", 403: "forbidden", 404: "not-found", 409: "conflict",
         422: "unprocessable", 429: "too-many-requests", 500: "internal-error", 502: "bad-gateway",
         503: "service-unavailable", 504: "gateway-timeout"}


class ApiError(Exception):
    def __init__(self, status, code, message):
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def raise_for_api(response):
    status = response.status_code
    if status < 400:
        return response
    code = CODES.get(status, f"http-{status}")
    try:
        reason = HTTPStatus(status).phrase
    except ValueError:
        reason = f"HTTP {status}"
    message = reason
    try:
        data = response.json()
    except ValueError:
        data = None
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            code = error.get("code") or code
            message = error.get("message") or message
        elif isinstance(error, str):
            message = error
        elif isinstance(data.get("detail"), str):
            message = data["detail"]
    raise ApiError(status, code, message)
