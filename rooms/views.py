import logging
import time

from django.http import HttpResponse
from django.shortcuts import render
from .services import get_all_rooms


logger = logging.getLogger("app")


def room_list(request):
    rooms = get_all_rooms()

    logger.info(
        "Room list requested",
        extra={
            "path": request.path,
            "method": request.method,
            "status_code": 200,
        },
    )

    return render(request, 'rooms/room_list.html', {'rooms': rooms})


def slow_view(request):
    time.sleep(8)

    logger.info(
        "Slow request completed",
        extra={
            "path": request.path,
            "method": request.method,
            "status_code": 200,
        },
    )

    return HttpResponse("Slow request finished")