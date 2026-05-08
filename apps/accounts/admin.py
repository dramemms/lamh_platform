from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import User, generate_temp_password


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("LAMH Access", {
            "fields": ("role", "region", "cercle", "commune"),
        }),
        ("LAMH Sécurité", {
            "fields": (
                "must_change_password",
                "temporary_password_created_at",
                "last_password_change",
                "failed_login_attempts",
                "account_locked_until",
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("LAMH Access", {
            "fields": ("role", "region", "cercle", "commune"),
        }),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "region",
        "must_change_password",
        "is_staff",
        "is_active",
    )

    def save_model(self, request, obj, form, change):
        print("SAVE_MODEL EXECUTE POUR :", obj.username)

        if not change:
            temp_password = generate_temp_password()

            obj.set_password(temp_password)
            obj.must_change_password = True
            obj.temporary_password_created_at = timezone.now()

            super().save_model(request, obj, form, change)

            print("======================================")
            print("EMAIL CREATION COMPTE LAMH")
            print("Destinataire :", obj.email)
            print("Utilisateur :", obj.username)
            print("Mot de passe temporaire :", temp_password)
            print("======================================")

            if obj.email:
                send_mail(
                    subject="Votre compte LAMH Platform",
                    message=f"""
Bonjour {obj.first_name or obj.username},

Votre compte LAMH Platform a été créé.

Nom d'utilisateur : {obj.username}
Mot de passe temporaire : {temp_password}

Ce mot de passe expire dans 24 heures.

Lors de votre première connexion, vous devrez obligatoirement changer votre mot de passe.

Cordialement,
LAMH Platform
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )

        else:
            super().save_model(request, obj, form, change)