from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

from apps.accounts.utils import is_temporary_password_expired


class ForcePasswordChangeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            change_password_url = reverse("change_password")
            expired_url = reverse("temporary_password_expired")
            logout_url = reverse("logout")

            allowed_paths = [
                change_password_url,
                expired_url,
                logout_url,
            ]

            if (
                request.user.must_change_password
                and is_temporary_password_expired(request.user)
            ):
                logout(request)
                return redirect("temporary_password_expired")

            if (
                request.user.must_change_password
                and request.path not in allowed_paths
            ):
                return redirect("change_password")

        return self.get_response(request)