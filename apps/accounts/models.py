from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group

import secrets
import string


class User(AbstractUser):

    ROLE_ADMIN = "ADMIN"
    ROLE_SUPERVISOR = "SUPERVISOR"
    ROLE_PROJECT_MANAGER = "PROJECT_MANAGER"
    ROLE_TECH_VALIDATOR = "TECH_VALIDATOR"
    ROLE_TECH_VERIFIER = "TECH_VERIFIER"
    ROLE_DATA_ENTRY = "DATA_ENTRY"
    ROLE_VIEWER = "VIEWER"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrateur"),
        (ROLE_SUPERVISOR, "Superviseur"),
        (ROLE_PROJECT_MANAGER, "Project Manager"),
        (ROLE_TECH_VALIDATOR, "Validateur technique"),
        (ROLE_TECH_VERIFIER,"Verification technique"),
        (ROLE_DATA_ENTRY, "Agent de saisie"),
        (ROLE_VIEWER, "Lecteur"),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default=ROLE_VIEWER,
    )

    region = models.ForeignKey(
        "geo.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    cercle = models.ForeignKey(
        "geo.Cercle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    commune = models.ForeignKey(
        "geo.Commune",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # ==============================
    # SECURITE MOT DE PASSE
    # ==============================

    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Doit changer le mot de passe"
    )

    temporary_password_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date création mot de passe temporaire"
    )

    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier changement mot de passe"
    )

    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentatives échouées"
    )

    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Compte verrouillé jusqu'à"
    )

    # ==============================
    # INFOS SYSTEME
    # ==============================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ==============================
    # METHODES
    # ==============================

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_supervisor(self):
        return self.role == self.ROLE_SUPERVISOR

    @property
    def is_project_manager(self):
        return self.role == self.ROLE_PROJECT_MANAGER

    @property
    def is_tech_validator(self):
        return self.role == self.ROLE_TECH_VALIDATOR

    @property
    def is_data_entry(self):
        return self.role == self.ROLE_DATA_ENTRY

    @property
    def is_viewer(self):
        return self.role == self.ROLE_VIEWER

    def password_is_expired(self):

        if not self.temporary_password_created_at:
            return False

        expiration_delay = timezone.timedelta(hours=24)

        return (
            timezone.now()
            > self.temporary_password_created_at + expiration_delay
        )

    def lock_account(self, minutes=30):

        self.account_locked_until = (
            timezone.now() + timezone.timedelta(minutes=minutes)
        )

        self.save()

    def unlock_account(self):

        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()

    def is_account_locked(self):

        if not self.account_locked_until:
            return False

        return timezone.now() < self.account_locked_until


# =====================================
# GENERATION MOT DE PASSE TEMPORAIRE
# =====================================

def generate_temp_password(length=12):

    chars = (
        string.ascii_letters
        + string.digits
        + "!@#$%"
    )

    return ''.join(
        secrets.choice(chars)
        for _ in range(length)
    )

class LAMHAccessGroup(models.Model):
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="lamh_access"
    )

    users = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name="lamh_access_groups"
    )

    regions = models.ManyToManyField("geo.Region", blank=True)
    cercles = models.ManyToManyField("geo.Cercle", blank=True)
    communes = models.ManyToManyField("geo.Commune", blank=True)

    can_access_accidents = models.BooleanField(default=True)
    can_access_victims = models.BooleanField(default=True)
    can_access_eree = models.BooleanField(default=True)
    can_access_reporting = models.BooleanField(default=False)
    can_view_all_regions = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group.name