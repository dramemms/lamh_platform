from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ValidationWorkflowMixin(models.Model):
    # =========================
    # STATUTS
    # =========================
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_TECH_VERIFIED = "TECH_VERIFIED"
    STATUS_TECH_VALIDATED = "TECH_VALIDATED"
    STATUS_PROGRAM_VALIDATED = "PROGRAM_VALIDATED"
    STATUS_RETURNED_FOR_CORRECTION = "RETURNED_FOR_CORRECTION"
    STATUS_APPROVED = "APPROVED"

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, "Soumis"),
        (STATUS_TECH_VERIFIED, "Vérification technique"),
        (STATUS_TECH_VALIDATED, "Validation technique"),
        (STATUS_PROGRAM_VALIDATED, "Validation programme"),
        (STATUS_RETURNED_FOR_CORRECTION, "Retourné pour correction"),
        (STATUS_APPROVED, "Approuvé"),
    ]

    # =========================
    # CHAMPS
    # =========================
    status = models.CharField(
        "Statut de validation",
        max_length=40,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED,
        db_index=True,
    )

    submitted_at = models.DateTimeField("Soumis le", blank=True, null=True)

    tech_verified_at = models.DateTimeField(
        "Vérifié techniquement le",
        blank=True,
        null=True,
    )

    tech_validated_at = models.DateTimeField(
        "Validé techniquement le",
        blank=True,
        null=True,
    )

    program_validated_at = models.DateTimeField(
        "Validé programme le",
        blank=True,
        null=True,
    )

    approved_at = models.DateTimeField("Approuvé le", blank=True, null=True)

    tech_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_tech_verified",
    )

    tech_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_tech_validated",
    )

    program_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_program_validated",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_approved",
    )

    rejection_reason = models.TextField(blank=True, null=True)
    correction_comment = models.TextField(blank=True, null=True)
    validation_comment = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    # =========================
    # TRANSITIONS AUTORISÉES
    # =========================
    @classmethod
    def allowed_transitions(cls):
        return {
            cls.STATUS_SUBMITTED: {
                cls.STATUS_TECH_VERIFIED,
                cls.STATUS_RETURNED_FOR_CORRECTION,
            },

            cls.STATUS_TECH_VERIFIED: {
                cls.STATUS_TECH_VALIDATED,
                cls.STATUS_RETURNED_FOR_CORRECTION,
            },

            cls.STATUS_TECH_VALIDATED: {
                cls.STATUS_PROGRAM_VALIDATED,
                cls.STATUS_RETURNED_FOR_CORRECTION,
            },

            cls.STATUS_PROGRAM_VALIDATED: {
                cls.STATUS_APPROVED,
                cls.STATUS_TECH_VALIDATED,
                cls.STATUS_RETURNED_FOR_CORRECTION,
            },

            cls.STATUS_RETURNED_FOR_CORRECTION: {
                cls.STATUS_SUBMITTED,
            },

            cls.STATUS_APPROVED: set(),
        }

    # =========================
    # VERIFICATION TRANSITION
    # =========================
    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.allowed_transitions().get(
            self.status,
            set(),
        )

    # =========================
    # TRANSITION PRINCIPALE
    # =========================
    def transition_to(
        self,
        new_status: str,
        user=None,
        reason: str = "",
        comment: str = "",
    ):
        if new_status == self.status:
            return

        if not self.can_transition_to(new_status):
            raise ValidationError(
                f"Transition interdite : {self.status} -> {new_status}"
            )

        now = timezone.now()

        if new_status == self.STATUS_SUBMITTED:
            self.submitted_at = now
            self.rejection_reason = ""
            self.correction_comment = ""

        elif new_status == self.STATUS_TECH_VERIFIED:
            self.tech_verified_by = user
            self.tech_verified_at = now
            self.rejection_reason = ""
            self.correction_comment = ""
            self.validation_comment = comment or "Vérification technique effectuée."

        elif new_status == self.STATUS_TECH_VALIDATED:
            self.tech_validated_by = user
            self.tech_validated_at = now
            self.rejection_reason = ""
            self.correction_comment = ""
            self.validation_comment = comment or "Validation technique effectuée."

        elif new_status == self.STATUS_PROGRAM_VALIDATED:
            self.program_validated_by = user
            self.program_validated_at = now
            self.rejection_reason = ""
            self.correction_comment = ""
            self.validation_comment = comment or "Validation programme effectuée."

        elif new_status == self.STATUS_RETURNED_FOR_CORRECTION:
            final_comment = comment or reason

            if not final_comment:
                raise ValidationError(
                    "Le commentaire de correction est obligatoire."
                )

            self.rejection_reason = reason or final_comment
            self.correction_comment = final_comment

        elif new_status == self.STATUS_APPROVED:
            self.approved_by = user
            self.approved_at = now
            self.rejection_reason = ""
            self.correction_comment = ""
            self.validation_comment = comment or "Approbation finale effectuée."

        self.status = new_status
        self.save()

    # =========================
    # HELPERS
    # =========================
    @property
    def is_approved(self) -> bool:
        return self.status == self.STATUS_APPROVED

    @property
    def is_fully_approved(self) -> bool:
        return self.status == self.STATUS_APPROVED