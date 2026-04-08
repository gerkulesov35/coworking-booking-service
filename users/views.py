import logging

from django.shortcuts import render


logger = logging.getLogger("app")


def profile_view(request):
    logger.info(
        "Profile page requested",
        extra={
            "path": request.path,
            "method": request.method,
            "status_code": 200,
        },
    )

    return render(request, 'users/profile.html')
