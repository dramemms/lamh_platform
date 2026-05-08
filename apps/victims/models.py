from django.db import models
from django.conf import settings

from apps.geo.models import Region, Cercle, Commune
from apps.incidents.models import Accident
from apps.core.models_workflow import ValidationWorkflowMixin


class Victim(ValidationWorkflowMixin, models.Model):
    accident = models.ForeignKey(
        Accident,
        on_delete=models.CASCADE,
        related_name="victims",
        verbose_name="Accident",
    )

    victim_id = models.CharField("ID de la victime", max_length=100, unique=True)
    report_date = models.DateField("Date du rapport", blank=True, null=True)
    accident_reference = models.CharField(
        "Référence de l'accident",
        max_length=100,
        blank=True,
        null=True,
    )

    reported_by = models.CharField("Rapporté par", max_length=255, blank=True, null=True)
    reporting_org = models.CharField("Organisation", max_length=255, blank=True, null=True)
    reporting_position = models.CharField("Poste", max_length=255, blank=True, null=True)
    reporting_team = models.CharField("Equipe", max_length=255, blank=True, null=True)

    consentement = models.BooleanField("Consentement", default=True)
    no_consent_reason = models.TextField("Raison du non consentement", blank=True, null=True)

    victim_last_name = models.CharField("Nom de la victime", max_length=150)
    victim_first_name = models.CharField("Prénom de la victime", max_length=150, blank=True, null=True)

    victim_type = models.CharField("Type de victime", max_length=100, blank=True, null=True)
    victim_type_other = models.CharField("Préciser type de victime", max_length=255, blank=True, null=True)

    father_name = models.CharField("Nom du père", max_length=150, blank=True, null=True)
    mother_name = models.CharField("Nom de la mère", max_length=150, blank=True, null=True)

    nationality = models.CharField("Nationalité", max_length=100, blank=True, null=True)
    nationality_other = models.CharField("Autre nationalité", max_length=255, blank=True, null=True)

    marital_status = models.CharField("Statut matrimonial", max_length=100, blank=True, null=True)

    profession_before = models.CharField(
        "Profession avant l'accident",
        max_length=100,
        blank=True,
        null=True,
    )
    profession_before_other = models.CharField(
        "Préciser profession avant",
        max_length=255,
        blank=True,
        null=True,
    )

    profession_after = models.CharField(
        "Profession après l'accident",
        max_length=100,
        blank=True,
        null=True,
    )
    profession_after_other = models.CharField(
        "Préciser profession après",
        max_length=255,
        blank=True,
        null=True,
    )

    outcome_type = models.CharField(
        "Tué / Blessé / impacté",
        max_length=50,
        blank=True,
        null=True,
    )

    birth_date_known = models.BooleanField("Date de naissance connue", default=False)
    birth_date = models.DateField("Date de naissance", blank=True, null=True)
    birth_date_approx = models.CharField(
        "Date de naissance approximative",
        max_length=100,
        blank=True,
        null=True,
    )
    victim_age = models.PositiveIntegerField("Âge", blank=True, null=True)
    victim_sex = models.CharField("Sexe", max_length=10, blank=True, null=True)

    main_breadwinner = models.BooleanField("Principal soutien de famille", default=False)
    dependents_count = models.PositiveIntegerField("Personnes à charge", blank=True, null=True)

    urgent_medical_evac = models.BooleanField(
        "Besoin d'évacuation / prise en charge médicale immédiate",
        default=False,
    )
    victim_contact = models.CharField("Contact", max_length=100, blank=True, null=True)

    activity_at_accident = models.CharField(
        "Activité au moment de l'accident",
        max_length=100,
        blank=True,
        null=True,
    )
    activity_at_accident_other = models.CharField(
        "Autre activité au moment de l'accident",
        max_length=255,
        blank=True,
        null=True,
    )

    knew_danger_zone = models.BooleanField(
        "Connaissait la zone dangereuse",
        default=False,
    )
    reason_enter_zone = models.CharField(
        "Raison d'entrer dans la zone",
        max_length=100,
        blank=True,
        null=True,
    )
    reason_enter_zone_other = models.CharField(
        "Autre raison d'entrée",
        max_length=255,
        blank=True,
        null=True,
    )
    times_entered_zone = models.PositiveIntegerField(
        "Nombre de fois entrée dans la zone",
        blank=True,
        null=True,
    )
    saw_object = models.BooleanField("A vu l'objet", default=False)

    blast_cause = models.CharField("Cause de l'explosion", max_length=100, blank=True, null=True)
    blast_cause_other = models.CharField("Autre cause", max_length=255, blank=True, null=True)
    alpc_type = models.CharField("Type d'ALPC", max_length=100, blank=True, null=True)
    alpc_type_other = models.CharField("Autre type d'ALPC", max_length=255, blank=True, null=True)

    received_er_before = models.BooleanField(
        "A reçu une session ER avant l'accident",
        default=False,
    )
    er_before_date = models.CharField(
        "Date approximative ER avant",
        max_length=100,
        blank=True,
        null=True,
    )

    received_er_after = models.BooleanField(
        "A reçu une session ER après l'accident",
        default=False,
    )
    er_after_date = models.CharField(
        "Date approximative ER après",
        max_length=100,
        blank=True,
        null=True,
    )
    er_org = models.CharField(
        "Organisation ayant délivré la session ER",
        max_length=255,
        blank=True,
        null=True,
    )

    pre_existing_disability = models.BooleanField(
        "Handicap avant l'accident",
        default=False,
    )
    disability_type_before = models.CharField(
        "Type de handicap avant l'accident",
        max_length=255,
        blank=True,
        null=True,
    )

    injury_type = models.CharField(
        "Type de blessure / traumatisme",
        max_length=255,
        blank=True,
        null=True,
    )
    loss_of = models.CharField("Perte de", max_length=255, blank=True, null=True)
    injury_description = models.TextField(
        "Description de la blessure / du traumatisme",
        blank=True,
        null=True,
    )

    health_structure = models.CharField(
        "Structure de santé",
        max_length=255,
        blank=True,
        null=True,
    )
    health_structure_other = models.CharField(
        "Autre structure de santé",
        max_length=255,
        blank=True,
        null=True,
    )

    medical_care = models.BooleanField("Prise en charge médicale", default=False)
    medical_care_date = models.CharField(
        "Date approximative prise en charge médicale",
        max_length=100,
        blank=True,
        null=True,
    )
    medical_org = models.CharField(
        "Organisation prise en charge médicale",
        max_length=255,
        blank=True,
        null=True,
    )

    non_medical_care = models.BooleanField("Prise en charge non médicale", default=False)
    non_medical_care_date = models.CharField(
        "Date approximative prise en charge non médicale",
        max_length=100,
        blank=True,
        null=True,
    )
    non_medical_org = models.CharField(
        "Organisation prise en charge non médicale",
        max_length=255,
        blank=True,
        null=True,
    )

    hours_to_first_medical_care = models.DecimalField(
        "Temps avant première prise en charge médicale (heures)",
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )

    info_source = models.CharField(
        "Source d'information",
        max_length=100,
        blank=True,
        null=True,
    )
    info_source_other = models.CharField("Autre source", max_length=255, blank=True, null=True)
    source_age = models.PositiveIntegerField("Age de la source", blank=True, null=True)
    source_last_name = models.CharField("Nom de la source", max_length=150, blank=True, null=True)
    source_first_name = models.CharField("Prénom de la source", max_length=150, blank=True, null=True)
    source_contact = models.CharField("Contact de la source", max_length=100, blank=True, null=True)
    source_sex = models.CharField("Sexe de la source", max_length=10, blank=True, null=True)

    country = models.CharField("Pays", max_length=100, blank=True, null=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="victim_reports",
        blank=True,
        null=True,
    )
    cercle = models.ForeignKey(
        Cercle,
        on_delete=models.PROTECT,
        related_name="victim_reports",
        blank=True,
        null=True,
    )
    commune = models.ForeignKey(
        Commune,
        on_delete=models.PROTECT,
        related_name="victim_reports",
        blank=True,
        null=True,
    )
    village_quartier = models.CharField("Village / Quartier", max_length=255, blank=True, null=True)
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6, blank=True, null=True)
    residence_place = models.CharField("Lieu de résidence", max_length=255, blank=True, null=True)
    address = models.TextField("Adresse", blank=True, null=True)
    location_details = models.TextField("Détails de l'emplacement", blank=True, null=True)

    kobo_submission_id = models.CharField(
        "Kobo Submission ID",
        max_length=100,
        blank=True,
        null=True,
    )
    kobo_uuid = models.CharField("Kobo UUID", max_length=255, blank=True, null=True)
    raw_payload = models.JSONField("Payload brut Kobo", blank=True, null=True)

    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        ordering = ["victim_last_name", "victim_first_name", "id"]
        verbose_name = "Victime"
        verbose_name_plural = "Victimes"

    def __str__(self):
        return f"{self.victim_last_name} {self.victim_first_name or ''}".strip()

    @property
    def victim_full_name(self):
        return f"{self.victim_last_name or ''} {self.victim_first_name or ''}".strip()


class VictimChangeLog(models.Model):
    victim = models.ForeignKey(
        "victims.Victim",
        on_delete=models.CASCADE,
        related_name="change_logs",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    workflow_step = models.CharField(max_length=100, blank=True, null=True)
    field_name = models.CharField(max_length=255)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Historique victime"
        verbose_name_plural = "Historiques victimes"

    def __str__(self):
        return f"{self.victim} - {self.field_name}"