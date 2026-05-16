from django.conf import settings
from django.db import models
from django.utils.timezone import now

from apps.geo.models import Region, Cercle, Commune
from apps.core.models_workflow import ValidationWorkflowMixin


class EREESession(ValidationWorkflowMixin, models.Model):
    # =========================
    # WORKFLOW
    # =========================
    STATUS_DRAFT = "DRAFT"
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_TECH_VALIDATED = "TECH_VALIDATED"
    STATUS_PROGRAM_VALIDATED = "PROGRAM_VALIDATED"
    STATUS_RETURNED_FOR_CORRECTION = "RETURNED_FOR_CORRECTION"
    STATUS_APPROVED = "APPROVED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_SUBMITTED, "Soumis"),
        (STATUS_TECH_VALIDATED, "Validé techniquement"),
        (STATUS_PROGRAM_VALIDATED, "Validé programme"),
        (STATUS_RETURNED_FOR_CORRECTION, "Retourné pour correction"),
        (STATUS_APPROVED, "Approuvé"),
    ]

    # =========================
    # IDENTIFICATION SYSTEME
    # =========================
    reference = models.CharField("Référence", max_length=100, unique=True)
    title = models.CharField("Titre", max_length=255, blank=True, null=True)

    # =========================
    # G_WEEKLY
    # =========================
    reported_by = models.CharField("Rapporté par", max_length=255, blank=True, null=True)
    week_number = models.PositiveIntegerField("Semaine", blank=True, null=True)
    week_from = models.DateField("Du", blank=True, null=True)
    week_to = models.DateField("Au", blank=True, null=True)
    month_name = models.CharField("Mois", max_length=50, blank=True, null=True)
    year = models.PositiveIntegerField("Année", blank=True, null=True)
    organisation = models.CharField("Organisation", max_length=255, blank=True, null=True)
    narrative_description = models.TextField(
        "Description narrative",
        blank=True,
        null=True,
    )

    # =========================
    # G_SESSION
    # =========================
    session_date = models.DateField("Date session", blank=True, null=True)
    location_gps = models.CharField("Coordonnées GPS", max_length=255, blank=True, null=True)
    latitude = models.DecimalField("Latitude", max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("Longitude", max_digits=10, decimal_places=6, blank=True, null=True)

    team = models.CharField("Équipe", max_length=100, blank=True, null=True)
    session_status = models.CharField("Statut session", max_length=100, blank=True, null=True)

    region_code = models.CharField("Code région Kobo", max_length=50, blank=True, null=True)
    cercle_code = models.CharField("Code cercle Kobo", max_length=50, blank=True, null=True)
    commune_code = models.CharField("Code commune Kobo", max_length=50, blank=True, null=True)

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="eree_sessions",
        verbose_name="Région",
        null=True,
        blank=True,
    )
    cercle = models.ForeignKey(
        Cercle,
        on_delete=models.PROTECT,
        related_name="eree_sessions",
        verbose_name="Cercle",
        null=True,
        blank=True,
    )
    commune = models.ForeignKey(
        Commune,
        on_delete=models.PROTECT,
        related_name="eree_sessions",
        verbose_name="Commune",
        null=True,
        blank=True,
    )

    village = models.CharField("Village", max_length=255, blank=True, null=True)
    methodology = models.CharField("Méthodologie", max_length=100, blank=True, null=True)
    sensitization_type = models.CharField("Type de sensibilisation", max_length=100, blank=True, null=True)
    civilian_subcategory = models.CharField("Sous-catégorie civils", max_length=100, blank=True, null=True)
    humanitarian_org_type = models.CharField(
        "Type organisation humanitaire",
        max_length=255,
        blank=True,
        null=True,
    )
    other_precision = models.CharField("Précision autres", max_length=255, blank=True, null=True)
    humanitarian_male = models.PositiveIntegerField("Humanitaire hommes", default=0)
    humanitarian_female = models.PositiveIntegerField("Humanitaire femmes", default=0)
    funding_type = models.CharField("Source de financement", max_length=100, blank=True, null=True)

    # =========================
    # G_PDI
    # =========================
    pdi_boys_0_5 = models.PositiveIntegerField(default=0)
    pdi_boys_0_5_dis = models.PositiveIntegerField(default=0)
    pdi_girls_0_5 = models.PositiveIntegerField(default=0)
    pdi_girls_0_5_dis = models.PositiveIntegerField(default=0)

    pdi_boys_6_14 = models.PositiveIntegerField(default=0)
    pdi_boys_6_14_dis = models.PositiveIntegerField(default=0)
    pdi_girls_6_14 = models.PositiveIntegerField(default=0)
    pdi_girls_6_14_dis = models.PositiveIntegerField(default=0)

    pdi_boys_15_17 = models.PositiveIntegerField(default=0)
    pdi_boys_15_17_dis = models.PositiveIntegerField(default=0)
    pdi_girls_15_17 = models.PositiveIntegerField(default=0)
    pdi_girls_15_17_dis = models.PositiveIntegerField(default=0)

    pdi_men_18_24 = models.PositiveIntegerField(default=0)
    pdi_men_18_24_dis = models.PositiveIntegerField(default=0)
    pdi_women_18_24 = models.PositiveIntegerField(default=0)
    pdi_women_18_24_dis = models.PositiveIntegerField(default=0)

    pdi_men_25_49 = models.PositiveIntegerField(default=0)
    pdi_men_25_49_dis = models.PositiveIntegerField(default=0)
    pdi_women_25_49 = models.PositiveIntegerField(default=0)
    pdi_women_25_49_dis = models.PositiveIntegerField(default=0)

    pdi_men_50_59 = models.PositiveIntegerField(default=0)
    pdi_men_50_59_dis = models.PositiveIntegerField(default=0)
    pdi_women_50_59 = models.PositiveIntegerField(default=0)
    pdi_women_50_59_dis = models.PositiveIntegerField(default=0)

    pdi_men_60_plus = models.PositiveIntegerField(default=0)
    pdi_men_60_plus_dis = models.PositiveIntegerField(default=0)
    pdi_women_60_plus = models.PositiveIntegerField(default=0)
    pdi_women_60_plus_dis = models.PositiveIntegerField(default=0)

    # =========================
    # G_CH
    # =========================
    ch_boys_0_5 = models.PositiveIntegerField(default=0)
    ch_boys_0_5_dis = models.PositiveIntegerField(default=0)
    ch_girls_0_5 = models.PositiveIntegerField(default=0)
    ch_girls_0_5_dis = models.PositiveIntegerField(default=0)

    ch_boys_6_14 = models.PositiveIntegerField(default=0)
    ch_boys_6_14_dis = models.PositiveIntegerField(default=0)
    ch_girls_6_14 = models.PositiveIntegerField(default=0)
    ch_girls_6_14_dis = models.PositiveIntegerField(default=0)

    ch_boys_15_17 = models.PositiveIntegerField(default=0)
    ch_boys_15_17_dis = models.PositiveIntegerField(default=0)
    ch_girls_15_17 = models.PositiveIntegerField(default=0)
    ch_girls_15_17_dis = models.PositiveIntegerField(default=0)

    ch_men_18_24 = models.PositiveIntegerField(default=0)
    ch_men_18_24_dis = models.PositiveIntegerField(default=0)
    ch_women_18_24 = models.PositiveIntegerField(default=0)
    ch_women_18_24_dis = models.PositiveIntegerField(default=0)

    ch_men_25_49 = models.PositiveIntegerField(default=0)
    ch_men_25_49_dis = models.PositiveIntegerField(default=0)
    ch_women_25_49 = models.PositiveIntegerField(default=0)
    ch_women_25_49_dis = models.PositiveIntegerField(default=0)

    ch_men_50_59 = models.PositiveIntegerField(default=0)
    ch_men_50_59_dis = models.PositiveIntegerField(default=0)
    ch_women_50_59 = models.PositiveIntegerField(default=0)
    ch_women_50_59_dis = models.PositiveIntegerField(default=0)

    ch_men_60_plus = models.PositiveIntegerField(default=0)
    ch_men_60_plus_dis = models.PositiveIntegerField(default=0)
    ch_women_60_plus = models.PositiveIntegerField(default=0)
    ch_women_60_plus_dis = models.PositiveIntegerField(default=0)

    leaflets_adults = models.PositiveIntegerField("Dépliants adultes", default=0)
    leaflets_children = models.PositiveIntegerField("Dépliants enfants", default=0)

    # =========================
    # G_QUALITY
    # =========================
    quality_date = models.DateField("Date qualité", blank=True, null=True)
    quality_team = models.CharField("Équipe qualité", max_length=100, blank=True, null=True)
    quality_method = models.CharField("Méthode qualité", max_length=100, blank=True, null=True)
    quality_observations = models.TextField("Observations qualité", blank=True, null=True)
    difficulties_solutions = models.TextField("Difficultés / solutions", blank=True, null=True)

    # =========================
    # TOTAUX
    # =========================
    total_pdi = models.PositiveIntegerField("Total PDI", default=0)
    total_host_community = models.PositiveIntegerField("Total communauté hôte", default=0)
    total_participants = models.PositiveIntegerField("Total participants", default=0)

    # =========================
    # KOBO / SYSTEME
    # =========================
    kobo_submission_id = models.CharField(
        "Kobo Submission ID",
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )
    kobo_uuid = models.CharField("Kobo UUID", max_length=255, blank=True, null=True)
    submitted_at_kobo = models.DateTimeField("Soumis dans Kobo le", blank=True, null=True)
    raw_payload = models.JSONField("Payload brut Kobo", blank=True, null=True)

    # =========================
    # WORKFLOW
    # =========================
    status = models.CharField(
        "Statut workflow",
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    validation_comment = models.TextField("Commentaire validation", blank=True, null=True)
    rejection_reason = models.TextField("Motif rejet", blank=True, null=True)
    correction_comment = models.TextField("Commentaire correction", blank=True, null=True)

    submitted_at = models.DateTimeField("Soumis le", blank=True, null=True)
    tech_validated_at = models.DateTimeField("Validé techniquement le", blank=True, null=True)
    program_validated_at = models.DateTimeField("Validé programme le", blank=True, null=True)
    approved_at = models.DateTimeField("Approuvé le", blank=True, null=True)

    tech_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eree_tech_validated",
    )
    program_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eree_program_validated",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eree_approved",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eree_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-session_date", "-created_at"]
        verbose_name = "Session EREE"
        verbose_name_plural = "Sessions EREE"

    def __str__(self):
        return self.reference or f"EREE-{self.pk}"

    def _sum_fields(self, field_names):
        return sum((getattr(self, name, 0) or 0) for name in field_names)

    def save(self, *args, **kwargs):
        if not self.reference and self.kobo_submission_id:
            self.reference = f"EREE-{self.kobo_submission_id}"

        if not self.title:
            self.title = f"EREE - {self.organisation or 'Sans organisation'}"

        pdi_fields = [
            "pdi_boys_0_5", "pdi_boys_0_5_dis", "pdi_girls_0_5", "pdi_girls_0_5_dis",
            "pdi_boys_6_14", "pdi_boys_6_14_dis", "pdi_girls_6_14", "pdi_girls_6_14_dis",
            "pdi_boys_15_17", "pdi_boys_15_17_dis", "pdi_girls_15_17", "pdi_girls_15_17_dis",
            "pdi_men_18_24", "pdi_men_18_24_dis", "pdi_women_18_24", "pdi_women_18_24_dis",
            "pdi_men_25_49", "pdi_men_25_49_dis", "pdi_women_25_49", "pdi_women_25_49_dis",
            "pdi_men_50_59", "pdi_men_50_59_dis", "pdi_women_50_59", "pdi_women_50_59_dis",
            "pdi_men_60_plus", "pdi_men_60_plus_dis", "pdi_women_60_plus", "pdi_women_60_plus_dis",
        ]
        ch_fields = [
            "ch_boys_0_5", "ch_boys_0_5_dis", "ch_girls_0_5", "ch_girls_0_5_dis",
            "ch_boys_6_14", "ch_boys_6_14_dis", "ch_girls_6_14", "ch_girls_6_14_dis",
            "ch_boys_15_17", "ch_boys_15_17_dis", "ch_girls_15_17", "ch_girls_15_17_dis",
            "ch_men_18_24", "ch_men_18_24_dis", "ch_women_18_24", "ch_women_18_24_dis",
            "ch_men_25_49", "ch_men_25_49_dis", "ch_women_25_49", "ch_women_25_49_dis",
            "ch_men_50_59", "ch_men_50_59_dis", "ch_women_50_59", "ch_women_50_59_dis",
            "ch_men_60_plus", "ch_men_60_plus_dis", "ch_women_60_plus", "ch_women_60_plus_dis",
        ]

        self.total_pdi = self._sum_fields(pdi_fields)
        self.total_host_community = self._sum_fields(ch_fields)
        self.total_participants = (
            self.total_pdi
            + self.total_host_community
            + (self.humanitarian_male or 0)
            + (self.humanitarian_female or 0)
        )

        if self.submitted_at and self.status == self.STATUS_DRAFT:
            self.status = self.STATUS_SUBMITTED

        if self.status == self.STATUS_SUBMITTED and not self.submitted_at:
            self.submitted_at = now()

        super().save(*args, **kwargs)

    @property
    def is_fully_approved(self):
        return self.status == self.STATUS_APPROVED

    def transition_to(self, new_status, user=None, reason=None, comment=None):
        allowed = {
            self.STATUS_DRAFT: {self.STATUS_SUBMITTED},
            self.STATUS_SUBMITTED: {
                self.STATUS_TECH_VALIDATED,
                self.STATUS_RETURNED_FOR_CORRECTION,
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

class EREESessionChangeLog(models.Model):
    session = models.ForeignKey(
        EREESession,
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
        verbose_name = "EREE change log"
        verbose_name_plural = "EREE change logs"

    def __str__(self):
        return f"{self.field_name} modifié par {self.changed_by}"
    

class EREEDisaggregation(models.Model):

    AGE_CHOICES = [
        ("0_5", "0-5 ans"),
        ("6_14", "6-14 ans"),
        ("15_17", "15-17 ans"),
        ("18_24", "18-24 ans"),
        ("25_49", "25-49 ans"),
        ("50_59", "50-59 ans"),
        ("60_plus", "60+ ans"),
    ]

    eree = models.ForeignKey(
        "EREESession",
        on_delete=models.CASCADE,
        related_name="disaggregations"
    )

    age_group = models.CharField(
        max_length=20,
        choices=AGE_CHOICES
    )

    # =====================================================
    # GARÇONS
    # =====================================================

    boys = models.PositiveIntegerField(default=0)

    boys_disabled = models.PositiveIntegerField(default=0)

    # =====================================================
    # HOMMES
    # =====================================================

    men = models.PositiveIntegerField(default=0)

    men_disabled = models.PositiveIntegerField(default=0)

    # =====================================================
    # FILLES
    # =====================================================

    girls = models.PositiveIntegerField(default=0)

    girls_disabled = models.PositiveIntegerField(default=0)

    # =====================================================
    # FEMMES
    # =====================================================

    women = models.PositiveIntegerField(default=0)

    women_disabled = models.PositiveIntegerField(default=0)

    # =====================================================
    # TOTAL
    # =====================================================

    @property
    def total(self):
        return (
            self.boys
            + self.boys_disabled
            + self.men
            + self.men_disabled
            + self.girls
            + self.girls_disabled
            + self.women
            + self.women_disabled
        )

    def __str__(self):
        return f"{self.eree} - {self.get_age_group_display()}"