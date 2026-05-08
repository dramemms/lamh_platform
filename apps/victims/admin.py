from django.contrib import admin
from .models import Victim


@admin.register(Victim)
class VictimAdmin(admin.ModelAdmin):
    list_display = (
        "victim_id",
        "accident",
        "victim_last_name",
        "victim_first_name",
        "victim_sex",
        "victim_age",
        "outcome_type",
        "profession_before",
        "created_at",
    )
    list_filter = (
        "victim_sex",
        "outcome_type",
        "main_breadwinner",
        "urgent_medical_evac",
        "medical_care",
        "non_medical_care",
        "region",
        "cercle",
        "commune",
        "created_at",
    )
    search_fields = (
        "victim_id",
        "victim_last_name",
        "victim_first_name",
        "accident__reference",
        "reported_by",
        "reporting_org",
        "victim_contact",
        "source_last_name",
        "source_first_name",
        "source_contact",
        "kobo_submission_id",
        "kobo_uuid",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("accident", "region", "cercle", "commune")

    fieldsets = (
        ("Lien avec l'accident", {
            "fields": ("accident", "accident_reference", "victim_id", "report_date")
        }),
        ("Informations générales du rapport", {
            "fields": (
                "reported_by",
                "reporting_org",
                "reporting_position",
                "reporting_team",
            )
        }),
        ("Consentement", {
            "fields": ("consentement", "no_consent_reason")
        }),
        ("Identité de la victime", {
            "fields": (
                "victim_last_name",
                "victim_first_name",
                "victim_type",
                "victim_type_other",
                "father_name",
                "mother_name",
                "nationality",
                "nationality_other",
                "marital_status",
            )
        }),
        ("Situation socio-économique", {
            "fields": (
                "profession_before",
                "profession_before_other",
                "profession_after",
                "profession_after_other",
                "main_breadwinner",
                "dependents_count",
            )
        }),
        ("Profil personnel", {
            "fields": (
                "birth_date_known",
                "birth_date",
                "birth_date_approx",
                "victim_age",
                "victim_sex",
                "victim_contact",
            )
        }),
        ("Conséquences de l'accident", {
            "fields": (
                "outcome_type",
                "urgent_medical_evac",
                "injury_type",
                "loss_of",
                "injury_description",
            )
        }),
        ("Circonstances de l'accident", {
            "fields": (
                "activity_at_accident",
                "activity_at_accident_other",
                "knew_danger_zone",
                "reason_enter_zone",
                "reason_enter_zone_other",
                "times_entered_zone",
                "saw_object",
                "blast_cause",
                "blast_cause_other",
                "alpc_type",
                "alpc_type_other",
            )
        }),
        ("Education aux risques / ER", {
            "fields": (
                "received_er_before",
                "er_before_date",
                "received_er_after",
                "er_after_date",
                "er_org",
            )
        }),
        ("Handicap et prise en charge", {
            "fields": (
                "pre_existing_disability",
                "disability_type_before",
                "health_structure",
                "health_structure_other",
                "medical_care",
                "medical_care_date",
                "medical_org",
                "non_medical_care",
                "non_medical_care_date",
                "non_medical_org",
                "hours_to_first_medical_care",
            )
        }),
        ("Source d'information", {
            "fields": (
                "info_source",
                "info_source_other",
                "source_age",
                "source_last_name",
                "source_first_name",
                "source_contact",
                "source_sex",
            )
        }),
        ("Localisation", {
            "fields": (
                "country",
                "region",
                "cercle",
                "commune",
                "village_quartier",
                "latitude",
                "longitude",
                "residence_place",
                "address",
                "location_details",
            )
        }),
        ("Source Kobo", {
            "fields": ("kobo_submission_id", "kobo_uuid", "raw_payload")
        }),
        ("Traçabilité", {
            "fields": ("created_at", "updated_at")
        }),
    )