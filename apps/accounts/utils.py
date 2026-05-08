from django.utils import timezone
from datetime import timedelta


def is_temporary_password_expired(user):
    if not user.must_change_password:
        return False

    if not user.temporary_password_created_at:
        return False

    expiration_time = user.temporary_password_created_at + timedelta(hours=24)

    return timezone.now() > expiration_time