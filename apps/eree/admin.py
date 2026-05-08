from django.contrib import admin
from .models import EREESession, EREESessionChangeLog


@admin.register(EREESession)
class EREESessionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "session_date",
        "title",
        "organisation",
        "reported_by",
        "team",
        "region",
        "cercle",
        "commune",
        "total_participants",
        "status",
    )

    list_filter = (
        "status",
        "organisation",
        "team",
        "region",
        "cercle",
        "commune",
        "session_date",
        "methodology",
        "sensitization_type",
        "funding_type",
        "quality_team",
        "quality_method",
    )

    search_fields = (
        "reference",
        "title",
        "organisation",
        "reported_by",
        "village",
        "narrative_description",
        "quality_observations",
        "difficulties_solutions",
        "kobo_submission_id",
        "kobo_uuid",
    )

    readonly_fields = (
        "total_pdi",
        "total_host_community",
        "total_participants",
        "submitted_at",
        "tech_validated_at",
        "program_validated_at",
        "approved_at",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = ("region", "cercle", "commune")

    fieldsets = (
        ("Identification système", {
            "fields": (
                "reference",
                "title",
                "kobo_submission_id",
                "kobo_uuid",
                "submitted_at_kobo",
            )
        }),
        ("Rapport hebdomadaire", {
            "fields": (
                "reported_by",
                "week_number",
                "week_from",
                "week_to",
                "month_name",
                "year",
                "organisation",
                "narrative_description",
            )
        }),
        ("Session EREE / EORE", {
            "fields": (
                "session_date",
                "location_gps",
                "latitude",
                "longitude",
                "team",
                "session_status",
                "region_code",
                "cercle_code",
                "commune_code",
                "region",
                "cercle",
                "commune",
                "village",
                "methodology",
                "sensitization_type",
                "civilian_subcategory",
                "humanitarian_org_type",
                "other_precision",
                "humanitarian_male",
                "humanitarian_female",
                "funding_type",
            )
        }),
        ("Bénéficiaires PDI", {
            "fields": (
                "pdi_boys_0_5",
                "pdi_boys_0_5_dis",
                "pdi_girls_0_5",
                "pdi_girls_0_5_dis",
                "pdi_boys_6_14",
                "pdi_boys_6_14_dis",
                "pdi_girls_6_14",
                "pdi_girls_6_14_dis",
                "pdi_boys_15_17",
                "pdi_boys_15_17_dis",
                "pdi_girls_15_17",
                "pdi_girls_15_17_dis",
                "pdi_men_18_24",
                "pdi_men_18_24_dis",
                "pdi_women_18_24",
                "pdi_women_18_24_dis",
                "pdi_men_25_49",
                "pdi_men_25_49_dis",
                "pdi_women_25_49",
                "pdi_women_25_49_dis",
                "pdi_men_50_59",
                "pdi_men_50_59_dis",
                "pdi_women_50_59",
                "pdi_women_50_59_dis",
                "pdi_men_60_plus",
                "pdi_men_60_plus_dis",
                "pdi_women_60_plus",
                "pdi_women_60_plus_dis",
                "total_pdi",
            )
        }),
        ("Bénéficiaires communauté hôte", {
            "fields": (
                "ch_boys_0_5",
                "ch_boys_0_5_dis",
                "ch_girls_0_5",
                "ch_girls_0_5_dis",
                "ch_boys_6_14",
                "ch_boys_6_14_dis",
                "ch_girls_6_14",
                "ch_girls_6_14_dis",
                "ch_boys_15_17",
                "ch_boys_15_17_dis",
                "ch_girls_15_17",
                "ch_girls_15_17_dis",
                "ch_men_18_24",
                "ch_men_18_24_dis",
                "ch_women_18_24",
                "ch_women_18_24_dis",
                "ch_men_25_49",
                "ch_men_25_49_dis",
                "ch_women_25_49",
                "ch_women_25_49_dis",
                "ch_men_50_59",
                "ch_men_50_59_dis",
                "ch_women_50_59",
                "ch_women_50_59_dis",
                "ch_men_60_plus",
                "ch_men_60_plus_dis",
                "ch_women_60_plus",
                "ch_women_60_plus_dis",
                "leaflets_adults",
                "leaflets_children",
                "total_host_community",
            )
        }),
        ("Rapport qualité", {
            "fields": (
                "quality_date",
                "quality_team",
                "quality_method",
                "quality_observations",
                "difficulties_solutions",
            )
        }),
        ("Workflow", {
            "fields": (
                "status",
                "validation_comment",
                "rejection_reason",
                "correction_comment",
                "submitted_at",
                "tech_validated_at",
                "tech_validated_by",
                "program_validated_at",
                "program_validated_by",
                "approved_at",
                "approved_by",
            )
        }),
        ("Traçabilité", {
            "fields": (
                "created_by",
                "created_at",
                "updated_at",
                "raw_payload",
            )
        }),
        ("Totaux", {
            "fields": (
                "total_participants",
            )
        }),
    )


@admin.register(EREESessionChangeLog)
class EREESessionChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "field_name",
        "changed_by",
        "workflow_step",
        "changed_at",
    )

    list_filter = (
        "workflow_step",
        "changed_at",
    )

    search_fields = (
        "session__reference",
        "field_name",
        "changed_by__username",
    )

    readonly_fields = (
        "session",
        "changed_by",
        "workflow_step",
        "field_name",
        "old_value",
        "new_value",
        "comment",
        "changed_at",
    )