# accounts/middleware.py

from django.shortcuts import redirect
from django.urls import reverse

from accounts.utils import is_temporary_password_expired


class ForcePasswordChangeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            # Vérifie expiration
            if (
                request.user.must_change_password
                and is_temporary_password_expired(request.user)
            ):

                from django.contrib.auth import logout
                logout(request)

                return redirect('temporary_password_expired')

            # Force changement mot de passe
            if (
                request.user.must_change_password
                and request.path != reverse('change_password')
            ):
                return redirect('change_password')

        return self.get_response(request)