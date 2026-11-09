import logging
import uuid

logger = logging.getLogger("inventory.requests")


class RequestIdMiddleware:
    def __init__(self, get_response):        # runs once, at server start
        self.get_response = get_response

    def __call__(self, request):             # runs for every request
        request.request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
        response = self.get_response(request)
        response["X-Request-Id"] = request.request_id
        logger.info("%s %s -> %s [%s]", request.method, request.path, response.status_code, request.request_id)
        return response
