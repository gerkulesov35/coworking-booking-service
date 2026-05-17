from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def manager_required(view_func):
    """Allow only users whose profile.role is manager or admin."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if profile is None or not profile.is_manager:
            raise PermissionDenied('Требуется роль менеджера или администратора.')
        return view_func(request, *args, **kwargs)

    return _wrapped
