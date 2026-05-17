import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm


logger = logging.getLogger("app")


@login_required
def profile_view(request):
    logger.info(
        "Profile page requested",
        extra={
            "path": request.path,
            "method": request.method,
            "status_code": 200,
        },
    )

    bookings_qs = request.user.bookings.select_related('room')
    recent_bookings = bookings_qs.order_by('-start_time')[:5]
    return render(request, 'users/profile.html', {
        'recent_bookings': recent_bookings,
        'bookings_total': bookings_qs.count(),
        'bookings_active': bookings_qs.exclude(status='cancelled').count(),
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Аккаунт создан.')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
