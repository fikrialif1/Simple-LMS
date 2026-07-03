from django.http import JsonResponse
from ninja.errors import HttpError


def api_success(message, data=None):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def api_error(status_code, message):
    raise HttpError(status_code, message)


def http_error_handler(request, exc):
    return JsonResponse(
        {
            "detail": {
                "success": False,
                "message": str(exc),
                "data": None
            }
        },
        status=exc.status_code
    )