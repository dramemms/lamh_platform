from django.conf import settings
from django.db import models
from django.utils.timezone import now

from apps.geo.models import Region, Cercle, Commune
from apps.core.models_workflow import ValidationWorkflowMixin


class Accident(ValidationWorkflowMixin, models.Model):
    # =========================
    # SOURCES
    # =========================
    SOURCE_KOBO = "KOBO"
    SOURCE_MANUAL = "MANUAL"
    SOURCE_API = "API"

    SOURCE_CHOICES = [
        (SOURCE_KOBO, "Kobo"),
        (SOURCE_MANUAL, "Saisie manuelle"),
        (SOURCE_API, "API"),
    ]

    # =========================
    # WORKFLOW COMPLET
    # =========================
    STATUS_DRAFT = "DRAFT"
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_TECH_VALIDATED = "TECH_VALIDATED"
    STATUS_PROGRAM_VALIDATED = "PROGRAM_VALIDATED"
    STATUS_APPROVED = "APPROVED"

    STATUS_CHOICES = [
    ("DRAFT", "Brouillon"),
    ("SUBMITTED", "Soumis"),
    ("TECH_VALIDATED", "Validé techniquement"),
    ("PROGRAM_VALIDATED", "Validé programme"),
    ("APPROVED", "Approuvé"),
    ("RETURNED_FOR_CORRECTION", "Retourné pour correction"),  # ✅
]

    # =========================
    # CATEGORIES / IMPACT
    # =========================
    CATEGORY_CHOICES = [
        ("ALPC", "ALPC"),
        ("MINE", "Mine"),
        ("ERW", "ERW / UXO"),
        ("IED", "IED"),
        ("ROAD", "Road"),
        ("OTHER", "Autre"),
    ]

    IMPACT_CHOICES = [
        ("NONE", "Aucun"),
        ("INJURY", "Blessure"),
        ("DEATH", "Décès"),
        ("DAMAGE", "Dommages matériels"),
        ("MULTIPLE", "Impacts multiples"),
    ]

    # =========================
    # IDENTIFICATION
    # =========================
    reference = models.CharField("Référence", max_length=50, unique=True)
    title = models.CharField("Titre", max_length=255, blank=True, null=True)
    description = models.TextField("Description", blank=True, null=True)

    # =========================
    # SOURCE / KOBO
    # =========================
    source = models.CharField(
        "Source",
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_KOBO,
    )
    kobo_submission_id = models.CharField(
        "Kobo Submission ID",
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )
    kobo_uuid = models.CharField("Kobo UUID", max_length=255, blank=True, null=True)
    kobo_asset_uid = models.CharField("Kobo Asset UID", max_length=255, blank=True, null=True)
    submitted_at_kobo = models.DateTimeField("Soumis dans Kobo le", blank=True, null=True)
    synced_at = models.DateTimeField("Synchronisé le", blank=True, null=True)
    is_synced = models.BooleanField("Synchronisé", default=False)
    raw_payload = models.JSONField("Payload brut Kobo", blank=True, null=True)

    # =========================
    # SOUMISSIONNAIRE
    # =========================
    submitter_email = models.EmailField("Email du soumissionnaire", blank=True, null=True)
    submitter_first_name = models.CharField(
        "Prénom du soumissionnaire",
        max_length=150,
        blank=True,
        null=True,
    )
    submitter_last_name = models.CharField(
        "Nom du soumissionnaire",
        max_length=150,
        blank=True,
        null=True,
    )
    submitter_phone = models.CharField(
        "Téléphone du soumissionnaire",
        max_length=50,
        blank=True,
        null=True,
    )
    submitter_organization = models.CharField(
        "Organisation du soumissionnaire",
        max_length=255,
        blank=True,
        null=True,
    )
    submitter_role = models.CharField(
        "Fonction du soumissionnaire",
        max_length=255,
        blank=True,
        null=True,
    )
    submitter_username = models.CharField(
        "Username Kobo / identifiant",
        max_length=150,
        blank=True,
        null=True,
    )

    # =========================
    # DETAILS ACCIDENT
    # =========================
    accident_date = models.DateField("Date de l'accident")
    accident_time = models.TimeField("Heure de l'accident", blank=True, null=True)

    category = models.CharField(
        "Type d'accident",
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="OTHER",
    )

    impact = models.CharField(
        "Impact principal",
        max_length=20,
        choices=IMPACT_CHOICES,
        blank=True,
        null=True,
    )

    number_victims = models.PositiveIntegerField(
        "Nombre de victimes",
        blank=True,
        null=True,
    )

    other_damage = models.CharField(
        "Autres dommages",
        max_length=255,
        blank=True,
        null=True,
    )
    activity_at_time = models.CharField(
        "Activité au moment de l'accident",
        max_length=255,
        blank=True,
        null=True,
    )

    device_type = models.CharField(
        "Type d'engin",
        max_length=255,
        blank=True,
        null=True,
    )
    device_status = models.CharField(
        "Statut de l'engin",
        max_length=255,
        blank=True,
        null=True,
    )
    device_marked = models.CharField(
        "Engin marqué",
        max_length=50,
        blank=True,
        null=True,
    )

    # =========================
    # LOCALISATION
    # =========================
    country = models.CharField("Pays", max_length=100, blank=True, null=True)

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="accidents",
        verbose_name="Région",
    )
    cercle = models.ForeignKey(
        Cercle,
        on_delete=models.PROTECT,
        related_name="accidents",
        verbose_name="Cercle",
    )
    commune = models.ForeignKey(
        Commune,
        on_delete=models.PROTECT,
        related_name="accidents",
        verbose_name="Commune",
    )

    locality = models.CharField("Localité / Village", max_length=255, blank=True, null=True)
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6, blank=True, null=True)

    secure_access = models.CharField("Accès sécurisé", max_length=50, blank=True, null=True)
    src_coordinates = models.CharField("Source des coordonnées", max_length=255, blank=True, null=True)
    location_gps = models.CharField("Coordonnées GPS brutes", max_length=255, blank=True, null=True)

    # =========================
    # REPORTING
    # =========================
    report_date = models.DateField("Date du rapport", blank=True, null=True)
    org_name = models.CharField("Organisation", max_length=255, blank=True, null=True)
    reported_by = models.CharField("Rapporté par", max_length=255, blank=True, null=True)
    position = models.CharField("Poste", max_length=255, blank=True, null=True)
    team = models.CharField("Équipe", max_length=255, blank=True, null=True)
    funding_source = models.CharField("Source de financement", max_length=255, blank=True, null=True)

    accident_associe_id = models.CharField(
        "ID accident associé",
        max_length=100,
        blank=True,
        null=True,
    )

    # =========================
    # SOURCE INFO
    # =========================
    source_name = models.CharField("Source / rapporté par", max_length=255, blank=True, null=True)
    source_contact = models.CharField("Contact source", max_length=100, blank=True, null=True)
    source_last_name = models.CharField("Nom de la source", max_length=150, blank=True, null=True)
    source_first_name = models.CharField("Prénom de la source", max_length=150, blank=True, null=True)
    source_gender = models.CharField("Sexe de la source", max_length=50, blank=True, null=True)
    source_age = models.PositiveIntegerField("Âge de la source", blank=True, null=True)
    source_type = models.CharField("Type de source", max_length=100, blank=True, null=True)

    # =========================
    # WORKFLOW
    # =========================
    status = models.CharField(
        "Statut",
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    validation_comment = models.TextField("Commentaire de validation", blank=True, null=True)
    rejection_reason = models.TextField("Motif de rejet", blank=True, null=True)
    correction_comment = models.TextField("Commentaire de correction", blank=True, null=True)

    submitted_at = models.DateTimeField("Soumis le", blank=True, null=True)

    tech_validated_at = models.DateTimeField("Validé techniquement le", blank=True, null=True)
    tech_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accidents_tech_validated",
        verbose_name="Validé techniquement par",
    )

    program_validated_at = models.DateTimeField("Validé programme le", blank=True, null=True)
    program_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accidents_program_validated",
        verbose_name="Validé programme par",
    )

    approved_at = models.DateTimeField("Approuvé le", blank=True, null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accidents_approved",
        verbose_name="Approuvé par",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accidents_created",
        verbose_name="Créé par",
    )

    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        ordering = ["-accident_date", "-created_at"]
        verbose_name = "Accident"
        verbose_name_plural = "Accidents"

    def __str__(self):
        return f"{self.reference} - {self.title or 'Accident'}"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"{self.reference} - {self.org_name or 'Accident'}"

        if self.submitted_at and self.status == self.STATUS_DRAFT:
            self.status = self.STATUS_SUBMITTED

        if self.status == self.STATUS_SUBMITTED and not self.submitted_at:
            self.submitted_at = now()

        super().save(*args, **kwargs)

    @property
    def submitter_full_name(self):
        parts = [self.submitter_first_name or "", self.submitter_last_name or ""]
        return " ".join(p for p in parts if p).strip()

    @property
    def is_fully_approved(self):
        return self.status == self.STATUS_APPROVED

    def transition_to(self, new_status, user=None, reason=None, comment=None):
        allowed = {
            self.STATUS_DRAFT: {self.STATUS_SUBMITTED},
            self.STATUS_SUBMITTED: {
    self.STATUS_TECH_VALIDATED,
    self.STATUS_RETURNED_FOR_CORRECTION,  # ✅ AJOUT
},
            self.STATUS_TECH_VALIDATED: {
                self.STATUS_PROGRAM_VALIDATED,
                self.STATUS_RETURNED_FOR_CORRECTION,
            },
            self.STATUS_PROGRAM_VALIDATED: {
                self.STATUS_APPROVED,
                self.STATUS_TECH_VALIDATED,
            },
            self.STATUS_RETURNED_FOR_CORRECTION: {
                self.STATUS_SUBMITTED,
            },
            self.STATUS_APPROVED: set(),
        }

        current = self.status

        if current not in allowed or new_status not in allowed[current]:
            raise ValueError(f"Transition non autorisée : {current} -> {new_status}")

        stamp = now()

        if new_status == self.STATUS_SUBMITTED:
            self.status = self.STATUS_SUBMITTED

            if not self.submitted_at:
                self.submitted_at = stamp

            if current == self.STATUS_RETURNED_FOR_CORRECTION:
                self.rejection_reason = None
                self.correction_comment = None

        elif new_status == self.STATUS_RETURNED_FOR_CORRECTION:
            self.status = self.STATUS_RETURNED_FOR_CORRECTION
            self.rejection_reason = reason or self.rejection_reason
            self.correction_comment = comment or reason or self.correction_comment

            self.tech_validated_at = None
            self.tech_validated_by = None
            self.program_validated_at = None
            self.program_validated_by = None
            self.approved_at = None
            self.approved_by = None

        elif new_status == self.STATUS_TECH_VALIDATED:
            self.status = self.STATUS_TECH_VALIDATED
            self.tech_validated_at = stamp
            self.tech_validated_by = user

            if current == self.STATUS_PROGRAM_VALIDATED:
                self.rejection_reason = reason or self.rejection_reason
                self.correction_comment = comment or reason or self.correction_comment
                self.program_validated_at = None
                self.program_validated_by = None
                self.approved_at = None
                self.approved_by = None
            else:
                self.rejection_reason = None
                self.correction_comment = None

        elif new_status == self.STATUS_PROGRAM_VALIDATED:
            self.status = self.STATUS_PROGRAM_VALIDATED
            self.program_validated_at = stamp
            self.program_validated_by = user
            self.rejection_reason = None
            self.correction_comment = None

        elif new_status == self.STATUS_APPROVED:
            self.status = self.STATUS_APPROVED
            self.approved_at = stamp
            self.approved_by = user
            self.rejection_reason = None
            self.correction_comment = None

        self.save()
        return self


class AccidentChangeLog(models.Model):
    accident = models.ForeignKey(
        Accident,
        on_delete=models.CASCADE,
        related_name="change_logs",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    workflow_step = models.CharField(max_length=50, blank=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Accident change log"
        verbose_name_plural = "Accident change logs"

    def __str__(self):
        return f"{self.field_name} modifié par {self.changed_by}"