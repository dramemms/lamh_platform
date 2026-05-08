from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Accident, AccidentChangeLog


@admin.action(description="Soumettre")
def mark_submitted(modeladmin, request, queryset):
    updated = 0
    for obj in queryset:
        try:
            obj.transition_to(obj.STATUS_SUBMITTED, user=request.user)
            updated += 1
        except (ValidationError, ValueError):
            continue
    messages.success(request, f"{updated} accident(s) soumis.")


@admin.action(description="Valider techniquement")
def mark_tech_validated(modeladmin, request, queryset):
    updated = 0
    for obj in queryset:
        try:
            obj.transition_to(obj.STATUS_TECH_VALIDATED, user=request.user)
            updated += 1
        except (ValidationError, ValueError):
            continue
    messages.success(request, f"{updated} accident(s) validé(s) techniquement.")


@admin.action(description="Valider programme")
def mark_program_validated(modeladmin, request, queryset):
    updated = 0
    for obj in queryset:
        try:
            obj.transition_to(obj.STATUS_PROGRAM_VALIDATED, user=request.user)
            updated += 1
        except (ValidationError, ValueError):
            continue
    messages.success(request, f"{updated} accident(s) validé(s) programme.")


@admin.action(description="Approuver")
def mark_approved(modeladmin, request, queryset):
    updated = 0
    for obj in queryset:
        try:
            obj.transition_to(obj.STATUS_APPROVED, user=request.user)
            updated += 1
        except (ValidationError, ValueError):
            continue
    messages.success(request, f"{updated} accident(s) approuvé(s).")


class AccidentChangeLogInline(admin.TabularInline):
    model = AccidentChangeLog
    extra = 0
    can_delete = False
    readonly_fields = (
        "workflow_step",
        "field_name",
        "old_value",
        "new_value",
        "comment",
        "changed_by",
        "changed_at",
    )


@admin.register(Accident)
class AccidentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "title",
        "accident_date",
        "category",
        "region",
        "commune",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
        "region",
        "cercle",
        "commune",
        "accident_date",
        "source",
        "is_synced",
    )

    search_fields = (
        "reference",
        "title",
        "description",
        "locality",
        "source_name",
        "source_contact",
        "submitter_email",
        "submitter_first_name",
        "submitter_last_name",
        "submitter_phone",
        "kobo_submission_id",
        "kobo_uuid",
        "reported_by",
        "org_name",
    )

    readonly_fields = (
        "submitted_at",
        "tech_validated_at",
        "program_validated_at",
        "approved_at",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "region",
        "cercle",
        "commune",
        "created_by",
        "tech_validated_by",
        "program_validated_by",
        "approved_by",
    )

    actions = [
        mark_submitted,
        mark_tech_validated,
        mark_program_validated,
        mark_approved,
    ]

    inlines = [AccidentChangeLogInline]

    fieldsets = (
        ("Identification", {
            "fields": (
                "reference",
                "title",
                
            )
        }),
        ("Source / Kobo", {
            "fields": (
                "source",
                "kobo_submission_id",
                "kobo_uuid",
                "kobo_asset_uid",
                "submitted_at_kobo",
                "synced_at",
                "is_synced",
                "raw_payload",
            )
        }),
        ("Soumissionnaire", {
            "fields": (
                "submitter_email",
                "submitter_first_name",
                "submitter_last_name",
                "submitter_phone",
                "submitter_organization",
                "submitter_role",
                "submitter_username",
            )
        }),
        ("Détails de l'accident", {
            "fields": (
                "accident_date",
                "accident_time",
                "category",
                "other_damage",
                "activity_at_time",
                "description",
                "device_type",
                "device_status",
                "device_marked",
                "number_victims",
            )
        }),
        ("Localisation", {
            "fields": (
                "country",
                "region",
                "cercle",
                "commune",
                "locality",
                "latitude",
                "longitude",
                "location_gps",
                "src_coordinates",
                "secure_access",
            )
        }),
        ("Source terrain", {
            "fields": (
                "source_name",
                "source_contact",
                "source_first_name",
                "source_last_name",
                "source_gender",
                "source_age",
                "source_type",
            )
        }),
        ("Rapport", {
            "fields": (
                "report_date",
                "org_name",
                "reported_by",
                "position",
                "team",
                "funding_source",
                "accident_associe_id",
            )
        }),
        ("Workflow de validation", {
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
            )
        }),
    )

    ordering = ("-accident_date", "-created_at")


@admin.register(AccidentChangeLog)
class AccidentChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        "accident",
        "field_name",
        "workflow_step",
        "changed_by",
        "changed_at",
    )
    list_filter = (
        "workflow_step",
        "changed_at",
    )
    search_fields = (
        "accident__reference",
        "accident__title",
        "field_name",
        "comment",
    )
    readonly_fields = (
        "accident",
        "workflow_step",
        "field_name",
        "old_value",
        "new_value",
        "comment",
        "changed_by",
        "changed_at",
    )
    ordering = ("-changed_at",)