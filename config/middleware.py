import logging
import uuid

from django.http import JsonResponse

from config import shutdown_state
from .logging import request_id_context


logger = logging.getLogger("app")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id
        request_id_context.set(request_id)

        if shutdown_state.is_shutting_down:
            logger.info(
                "Request rejected during shutdown",
                extra={
                    "path": request.path,
                    "method": request.method,
                    "status_code": 503,
                },
            )
            response = JsonResponse(
                {"detail": "Service is shutting down"},
                status=503,
            )
            response["X-Request-ID"] = request_id
            return response

        response = self.get_response(request)
        response["X-Request-ID"] = request_id

        logger.info(
            "HTTP request processed",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
            },
        )

        return response