import json
from urllib.parse import urlencode

import openpyxl
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, Case, When, Value, CharField, F
from django.db.models.functions import Lower, Trim
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import VictimEditForm, VictimForm
from .models import Victim, VictimChangeLog

from apps.core.permissions import (
    can_approve,
    can_edit_accident,
    can_program_validate,
    can_tech_validate,
    can_tech_verify,
)

from apps.incidents.models import Accident

from apps.notifications.services import (
    notify_victim_submitted,
    notify_victim_tech_validated,
    notify_victim_program_validated,
    notify_victim_returned,
    notify_victim_approved,
)

from .notifications import (
    notify_submitter_on_victim_approval,
    notify_submitter_on_victim_return,
)


class VictimWorkflowCommentForm(forms.Form):
    reason = forms.CharField(
        required=False,
        label="Motif",
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
    )

    comment = forms.CharField(
        required=False,
        label="Commentaire",
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
    )


def get_victim_base_queryset():
    return Victim.objects.select_related(
        "accident",
        "region",
        "cercle",
        "commune",
        "tech_verified_by",
        "tech_validated_by",
        "program_validated_by",
        "approved_by",
    )


def get_user_scoped_victim_queryset(user, with_logs=False):
    queryset = get_victim_base_queryset()

    if with_logs:
        queryset = queryset.prefetch_related("change_logs")

    if user.is_superuser:
        return queryset

    if getattr(user, "region", None):
        queryset = queryset.filter(region=user.region)

    if getattr(user, "cercle", None):
        queryset = queryset.filter(cercle=user.cercle)

    if getattr(user, "commune", None):
        queryset = queryset.filter(commune=user.commune)

    return queryset.distinct()


def get_victim_or_404(user, pk, with_logs=False):
    queryset = get_user_scoped_victim_queryset(user, with_logs=with_logs)
    return get_object_or_404(queryset, pk=pk)


def normalize_value(value):
    if value is None:
        return ""

    if hasattr(value, "pk"):
        return str(value.pk)

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value).strip()


def display_value(value):
    if value is None or value == "":
        return "-"

    if isinstance(value, bool):
        return "Oui" if value else "Non"

    return str(value)


def format_kobo_date(value):
    if not value:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")

    return str(value)


def safe_get(obj, *fields):
    for field in fields:
        if hasattr(obj, field):
            value = getattr(obj, field)

            if value not in [None, ""]:
                return value

    return ""


def get_workflow_step_label(victim):
    status_map = {
        Victim.STATUS_SUBMITTED: "Soumission",
        Victim.STATUS_TECH_VERIFIED: "Vérification technique",
        Victim.STATUS_TECH_VALIDATED: "Validation technique",
        Victim.STATUS_PROGRAM_VALIDATED: "Validation programme",
        Victim.STATUS_APPROVED: "Approbation finale",
    }

    if hasattr(Victim, "STATUS_RETURNED_FOR_CORRECTION"):
        status_map[Victim.STATUS_RETURNED_FOR_CORRECTION] = "Retour pour correction"

    return status_map.get(victim.status, victim.get_status_display())


@login_required
def victim_list(request):
    query = request.GET.get("q", "").strip()
    region_id = request.GET.get("region", "").strip()
    cercle_id = request.GET.get("cercle", "").strip()
    commune_id = request.GET.get("commune", "").strip()
    outcome_type = request.GET.get("outcome_type", "").strip()
    status = request.GET.get("status", "").strip()

    base_queryset = get_user_scoped_victim_queryset(request.user)
    victims = base_queryset

    if query:
        victims = victims.filter(
            Q(victim_id__icontains=query)
            | Q(victim_last_name__icontains=query)
            | Q(victim_first_name__icontains=query)
            | Q(accident_reference__icontains=query)
            | Q(village_quartier__icontains=query)
            | Q(source_last_name__icontains=query)
            | Q(source_first_name__icontains=query)
            | Q(reporting_org__icontains=query)
        )

    if region_id:
        victims = victims.filter(region_id=region_id)

    if cercle_id:
        victims = victims.filter(cercle_id=cercle_id)

    if commune_id:
        victims = victims.filter(commune_id=commune_id)

    if outcome_type:
        victims = victims.filter(outcome_type=outcome_type)

    allowed_statuses = {
        Victim.STATUS_SUBMITTED,
        Victim.STATUS_TECH_VERIFIED,
        Victim.STATUS_TECH_VALIDATED,
        Victim.STATUS_PROGRAM_VALIDATED,
        Victim.STATUS_APPROVED,
    }

    if hasattr(Victim, "STATUS_RETURNED_FOR_CORRECTION"):
        allowed_statuses.add(Victim.STATUS_RETURNED_FOR_CORRECTION)

    if status in allowed_statuses:
        victims = victims.filter(status=status)
    else:
        status = ""

    victims = victims.order_by("-created_at")

    context = {
        "victims": victims,
        "count": victims.count(),
        "count_all": base_queryset.count(),
        "count_submitted": base_queryset.filter(
            status=Victim.STATUS_SUBMITTED
        ).count(),
        "count_tech_verified": base_queryset.filter(
            status=Victim.STATUS_TECH_VERIFIED
        ).count(),
        "count_tech": base_queryset.filter(
            status=Victim.STATUS_TECH_VALIDATED
        ).count(),
        "count_program": base_queryset.filter(
            status=Victim.STATUS_PROGRAM_VALIDATED
        ).count(),
        "count_approved": base_queryset.filter(
            status=Victim.STATUS_APPROVED
        ).count(),
        "query": query,
        "selected_region": region_id,
        "selected_cercle": cercle_id,
        "selected_commune": commune_id,
        "selected_outcome_type": outcome_type,
        "current_status": status,
    }

    return render(request, "victims/victim_list.html", context)


@login_required
def victim_add(request, accident_id):
    accident = get_object_or_404(
        Accident.objects.select_related("region", "cercle", "commune"),
        pk=accident_id,
    )

    if not accident.is_fully_approved:
        messages.error(
            request,
            "Vous ne pouvez pas ajouter de victime tant que l'accident n'est pas entièrement approuvé.",
        )
        return redirect("accident_detail", pk=accident.pk)

    if request.method == "POST":
        form = VictimForm(request.POST)

        if form.is_valid():
            victim = form.save(commit=False)
            victim.accident = accident

            if hasattr(victim, "accident_reference"):
                victim.accident_reference = accident.reference

            if hasattr(victim, "region") and not victim.region_id:
                victim.region = accident.region

            if hasattr(victim, "cercle") and not victim.cercle_id:
                victim.cercle = accident.cercle

            if hasattr(victim, "commune") and not victim.commune_id:
                victim.commune = accident.commune

            if hasattr(victim, "status") and not victim.status:
                victim.status = Victim.STATUS_SUBMITTED

            victim.save()
            form.save_m2m()

            notify_victim_submitted(victim)

            messages.success(request, "Victime ajoutée avec succès.")
            return redirect("accident_detail", pk=accident.pk)

        messages.error(request, "Le formulaire contient des erreurs.")

    else:
        initial = {}

        if "accident_reference" in VictimForm.base_fields:
            initial["accident_reference"] = accident.reference

        if "region" in VictimForm.base_fields:
            initial["region"] = accident.region_id

        if "cercle" in VictimForm.base_fields:
            initial["cercle"] = accident.cercle_id

        if "commune" in VictimForm.base_fields:
            initial["commune"] = accident.commune_id

        form = VictimForm(initial=initial)

    return render(
        request,
        "victims/victim_form.html",
        {
            "form": form,
            "accident": accident,
        },
    )


@login_required
def victim_detail(request, pk):
    victim = get_victim_or_404(request.user, pk, with_logs=True)

    payload_pretty = ""

    if victim.raw_payload:
        try:
            payload_pretty = json.dumps(
                victim.raw_payload,
                indent=2,
                ensure_ascii=False,
            )
        except Exception:
            payload_pretty = str(victim.raw_payload)

    context = {
        "victim": victim,
        "payload_pretty": payload_pretty,
        "payload": victim.raw_payload,
        "can_edit_victim": can_edit_accident(request.user),
        "can_tech_verify": can_tech_verify(request.user),
        "can_tech_validate": can_tech_validate(request.user),
        "can_program_validate": can_program_validate(request.user),
        "can_approve": can_approve(request.user),
    }

    return render(request, "victims/victim_detail.html", context)


@login_required
def victim_edit(request, pk):
    victim = get_victim_or_404(request.user, pk)

    if not can_edit_accident(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("victim_detail", pk=pk)

    if victim.status == Victim.STATUS_APPROVED:
        messages.error(
            request,
            "Cette victime est approuvée et ne peut plus être modifiée.",
        )
        return redirect("victim_detail", pk=pk)

    if request.method == "POST":
        form = VictimEditForm(request.POST, instance=victim)

        if form.is_valid():
            comment = form.cleaned_data.get("comment", "").strip()

            old_victim = Victim.objects.get(pk=victim.pk)
            workflow_step_label = get_workflow_step_label(old_victim)

            old_values = {}

            for field_name in form.fields.keys():
                if field_name == "comment":
                    continue

                old_values[field_name] = getattr(old_victim, field_name, None)

            updated_victim = form.save(commit=False)
            real_changes = []

            for field_name in form.fields.keys():
                if field_name == "comment":
                    continue

                old_value = old_values.get(field_name)
                new_value = getattr(updated_victim, field_name, None)

                if normalize_value(old_value) != normalize_value(new_value):
                    field_label = form.fields[field_name].label or field_name

                    real_changes.append(
                        {
                            "field_name": field_label,
                            "old_value": display_value(old_value),
                            "new_value": display_value(new_value),
                        }
                    )

            if not real_changes:
                messages.info(request, "Aucune modification réelle détectée.")
                return redirect("victim_detail", pk=pk)

            updated_victim.save()
            form.save_m2m()

            for change in real_changes:
                VictimChangeLog.objects.create(
                    victim=updated_victim,
                    changed_by=request.user,
                    workflow_step=workflow_step_label,
                    field_name=change["field_name"],
                    old_value=change["old_value"],
                    new_value=change["new_value"],
                    comment=comment or "-",
                )

            messages.success(request, "Victime modifiée avec succès.")
            return redirect("victim_detail", pk=pk)

        messages.error(request, "Le formulaire contient des erreurs.")

    else:
        form = VictimEditForm(instance=victim)

    return render(
        request,
        "victims/victim_edit.html",
        {
            "victim": victim,
            "form": form,
        },
    )


@login_required
def victim_transition(request, pk, action):
    victim = get_victim_or_404(request.user, pk)

    try:
        if action == "submit":
            if not can_edit_accident(request.user):
                raise ValidationError("Non autorisé.")

            if victim.status != Victim.STATUS_RETURNED_FOR_CORRECTION:
                raise ValidationError("Transition invalide.")

            victim.transition_to(
                Victim.STATUS_SUBMITTED,
                user=request.user,
                comment="Fiche victime corrigée et ressoumise.",
            )

            notify_victim_submitted(victim)
            messages.success(request, "La fiche victime a été ressoumise avec succès.")

        elif action == "tech_verify":
            if not can_tech_verify(request.user):
                raise ValidationError("Non autorisé.")

            if victim.status != Victim.STATUS_SUBMITTED:
                raise ValidationError("Transition invalide.")

            victim.transition_to(
                Victim.STATUS_TECH_VERIFIED,
                user=request.user,
                comment="Vérification technique effectuée.",
            )

            messages.success(request, "Vérification technique effectuée.")

        elif action == "tech_validate":
            if not can_tech_validate(request.user):
                raise ValidationError("Non autorisé.")

            if victim.status != Victim.STATUS_TECH_VERIFIED:
                raise ValidationError("Transition invalide.")

            victim.transition_to(
                Victim.STATUS_TECH_VALIDATED,
                user=request.user,
                comment="Validation technique effectuée.",
            )

            notify_victim_tech_validated(victim)
            messages.success(request, "Validation technique effectuée.")

        elif action == "program_validate":
            if not can_program_validate(request.user):
                raise ValidationError("Non autorisé.")

            if victim.status != Victim.STATUS_TECH_VALIDATED:
                raise ValidationError("Transition invalide.")

            victim.transition_to(
                Victim.STATUS_PROGRAM_VALIDATED,
                user=request.user,
                comment="Validation programme effectuée.",
            )

            notify_victim_program_validated(victim)
            messages.success(request, "Validation programme effectuée.")

        elif action == "approve":
            if not can_approve(request.user):
                raise ValidationError("Non autorisé.")

            if victim.status != Victim.STATUS_PROGRAM_VALIDATED:
                raise ValidationError("Transition invalide.")

            victim.transition_to(
                Victim.STATUS_APPROVED,
                user=request.user,
                comment="Approbation finale effectuée.",
            )

            notify_victim_approved(victim)
            notify_submitter_on_victim_approval(victim)

            messages.success(request, "Approbation finale effectuée.")

        else:
            raise ValidationError("Action inconnue.")

    except (ValidationError, ValueError) as e:
        messages.error(request, str(e))

    return redirect("victim_detail", pk=pk)


@login_required
def victim_reject_or_return(request, pk, action):
    victim = get_victim_or_404(request.user, pk)

    if action not in {"tech_reject", "program_reject"}:
        messages.error(request, "Action inconnue.")
        return redirect("victim_detail", pk=pk)

    form = VictimWorkflowCommentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            reason = (form.cleaned_data.get("reason") or "").strip()
            comment = (form.cleaned_data.get("comment") or "").strip()
            final_comment = comment or reason

            if not final_comment:
                messages.error(request, "Le motif / commentaire est obligatoire.")
                return render(
                    request,
                    "victims/victim_workflow_form.html",
                    {
                        "victim": victim,
                        "form": form,
                        "action": action,
                        "title": "Retour au soumissionnaire"
                        if action == "tech_reject"
                        else "Retour à la validation technique",
                    },
                )

            if action == "tech_reject":
                if not (
                    can_tech_verify(request.user)
                    or can_tech_validate(request.user)
                ):
                    raise ValidationError("Action non autorisée.")

                if victim.status not in [
                    Victim.STATUS_SUBMITTED,
                    Victim.STATUS_TECH_VERIFIED,
                ]:
                    raise ValidationError("Transition invalide.")

                victim.transition_to(
                    Victim.STATUS_RETURNED_FOR_CORRECTION,
                    user=request.user,
                    reason=reason,
                    comment=final_comment,
                )

                notify_submitter_on_victim_return(victim)
                notify_victim_returned(victim)

                messages.success(
                    request,
                    "La victime a été retournée au soumissionnaire.",
                )

                return redirect("victim_detail", pk=pk)

            elif action == "program_reject":
                if not can_program_validate(request.user) and not can_approve(request.user):
                    raise ValidationError("Action non autorisée.")

                if victim.status == Victim.STATUS_PROGRAM_VALIDATED:
                    victim.transition_to(
                        Victim.STATUS_TECH_VALIDATED,
                        user=request.user,
                        reason=reason,
                        comment=final_comment,
                    )

                    notify_victim_returned(victim)

                    messages.success(
                        request,
                        "La victime a été retournée à la validation technique.",
                    )

                    return redirect("victim_detail", pk=pk)

                if victim.status == Victim.STATUS_TECH_VALIDATED:
                    victim.transition_to(
                        Victim.STATUS_RETURNED_FOR_CORRECTION,
                        user=request.user,
                        reason=reason,
                        comment=final_comment,
                    )

                    notify_victim_returned(victim)
                    notify_submitter_on_victim_return(victim)

                    messages.success(
                        request,
                        "La victime a été retournée au soumissionnaire.",
                    )

                    return redirect("victim_detail", pk=pk)

                raise ValidationError("Transition invalide.")

        except (ValidationError, ValueError) as e:
            messages.error(request, str(e))

    return render(
        request,
        "victims/victim_workflow_form.html",
        {
            "victim": victim,
            "form": form,
            "action": action,
            "title": "Retour au soumissionnaire"
            if action == "tech_reject"
            else "Retour à la validation technique",
        },
    )


@login_required
def victim_resubmit(request, pk):
    return victim_transition(request, pk, "submit")


@login_required
def victim_tech_verify(request, pk):
    return victim_transition(request, pk, "tech_verify")


@login_required
def victim_tech_validate(request, pk):
    return victim_transition(request, pk, "tech_validate")


@login_required
def victim_program_validate(request, pk):
    return victim_transition(request, pk, "program_validate")


@login_required
def victim_approve(request, pk):
    return victim_transition(request, pk, "approve")


@login_required
def victim_tech_reject(request, pk):
    return victim_reject_or_return(request, pk, "tech_reject")


@login_required
def victim_program_reject(request, pk):
    return victim_reject_or_return(request, pk, "program_reject")


@login_required
def victim_send_to_program(request, pk):
    victim = get_victim_or_404(request.user, pk)

    if not can_tech_validate(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("victim_detail", pk=pk)

    if victim.status != Victim.STATUS_TECH_VALIDATED:
        messages.error(request, "Transition invalide.")
        return redirect("victim_detail", pk=pk)

    notify_victim_tech_validated(victim)

    messages.success(
        request,
        "La victime a été resoumise au Programme Manager.",
    )

    return redirect("victim_detail", pk=pk)


@login_required
def export_victims_excel(request):
    query = request.GET.get("q", "").strip()
    region_id = request.GET.get("region", "").strip()
    cercle_id = request.GET.get("cercle", "").strip()
    commune_id = request.GET.get("commune", "").strip()
    outcome_type = request.GET.get("outcome_type", "").strip()
    status = request.GET.get("status", "").strip()

    victims = get_user_scoped_victim_queryset(request.user).filter(
        status=Victim.STATUS_APPROVED
    )

    if query:
        victims = victims.filter(
            Q(victim_id__icontains=query)
            | Q(victim_last_name__icontains=query)
            | Q(victim_first_name__icontains=query)
            | Q(accident_reference__icontains=query)
            | Q(village_quartier__icontains=query)
            | Q(source_last_name__icontains=query)
            | Q(source_first_name__icontains=query)
            | Q(reporting_org__icontains=query)
        )

    if region_id:
        victims = victims.filter(region_id=region_id)

    if cercle_id:
        victims = victims.filter(cercle_id=cercle_id)

    if commune_id:
        victims = victims.filter(commune_id=commune_id)

    if outcome_type:
        victims = victims.filter(outcome_type=outcome_type)

    allowed_statuses = {
        Victim.STATUS_SUBMITTED,
        Victim.STATUS_TECH_VERIFIED,
        Victim.STATUS_TECH_VALIDATED,
        Victim.STATUS_PROGRAM_VALIDATED,
        Victim.STATUS_APPROVED,
    }

    if hasattr(Victim, "STATUS_RETURNED_FOR_CORRECTION"):
        allowed_statuses.add(Victim.STATUS_RETURNED_FOR_CORRECTION)

    if status in allowed_statuses:
        victims = victims.filter(status=status)

    victims = victims.order_by("-created_at")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Victimes"

    excluded_fields = [
        "raw_payload",
        "kobo_uuid",
        "kobo_asset_uid",
        "kobo_submission_id",
        "is_synced",
        "synced_at",
    ]

    fields = [
        field
        for field in Victim._meta.fields
        if field.name not in excluded_fields
    ]

    ws.append([field.verbose_name.title() for field in fields])

    for v in victims:
        row = []

        for field in fields:
            field_name = field.name
            value = getattr(v, field_name, "")

            if field_name == "status":
                value = v.get_status_display()

            elif field_name == "accident":
                value = v.accident.reference if v.accident else ""

            elif field_name == "region":
                value = v.region.name if v.region else ""

            elif field_name == "cercle":
                value = v.cercle.name if v.cercle else ""

            elif field_name == "commune":
                value = v.commune.name if v.commune else ""

            elif field_name == "tech_verified_by":
                value = str(v.tech_verified_by) if v.tech_verified_by else ""

            elif field_name == "tech_validated_by":
                value = str(v.tech_validated_by) if v.tech_validated_by else ""

            elif field_name == "program_validated_by":
                value = str(v.program_validated_by) if v.program_validated_by else ""

            elif field_name == "approved_by":
                value = str(v.approved_by) if v.approved_by else ""

            elif isinstance(value, bool):
                value = "Oui" if value else "Non"

            elif hasattr(value, "strftime"):
                value = value.strftime("%d/%m/%Y %H:%M")

            elif hasattr(value, "pk"):
                value = str(value)

            row.append(value)

        ws.append(row)

    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[col_letter].width = min(max_length + 2, 60)

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = 'attachment; filename="victimes_complet.xlsx"'

    wb.save(response)

    return response



def victim_dashboard(request):
    victims = get_user_scoped_victim_queryset(request.user).filter(
        status=Victim.STATUS_APPROVED
    )

    organisation = request.GET.get("organisation", "").strip()
    accident_type = request.GET.get("accident_type", "").strip()
    region = request.GET.get("region", "").strip()
    cercle = request.GET.get("cercle", "").strip()
    commune = request.GET.get("commune", "").strip()
    periode = request.GET.get("periode", "").strip()

    if organisation and organisation.lower() != "tout":
        victims = victims.annotate(
            org_clean=Lower(Trim("reporting_org"))
        ).filter(
            org_clean=organisation.lower()
        )

    if accident_type and accident_type.lower() != "tout":
        victims = victims.filter(accident__category__iexact=accident_type)

    if region and region.lower() != "tout":
        victims = victims.filter(region_id=region)

    if cercle and cercle.lower() != "tout":
        victims = victims.filter(cercle_id=cercle)

    if commune and commune.lower() != "tout":
        victims = victims.filter(commune_id=commune)

    if periode and periode.lower() != "tout" and periode.isdigit():
        victims = victims.filter(report_date__year=int(periode))

    total = victims.count()

    masculin_q = (
        Q(victim_sex__iexact="male")
        | Q(victim_sex__iexact="masculin")
        | Q(victim_sex__iexact="m")
    )

    feminin_q = (
        Q(victim_sex__iexact="female")
        | Q(victim_sex__iexact="féminin")
        | Q(victim_sex__iexact="feminin")
        | Q(victim_sex__iexact="f")
    )

    masculin = victims.filter(masculin_q).count()
    feminin = victims.filter(feminin_q).count()

    masculin_pct = round((masculin / total * 100), 1) if total else 0
    feminin_pct = round((feminin / total * 100), 1) if total else 0

    by_accident_type = (
        victims.annotate(
            accident_type_label=Case(
                When(
                    Q(accident__category__isnull=False)
                    & ~Q(accident__category=""),
                    then=F("accident__category"),
                ),
                When(
                    Q(alpc_type__isnull=False)
                    & ~Q(alpc_type=""),
                    then=F("alpc_type"),
                ),
                default=Value("ALPC"),
                output_field=CharField(),
            )
        )
        .values("accident_type_label")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    by_status = (
        victims.annotate(
            victim_type_label=Case(
                When(
                    Q(victim_type__isnull=False)
                    & ~Q(victim_type=""),
                    then=F("victim_type"),
                ),
                When(
                    Q(outcome_type__isnull=False)
                    & ~Q(outcome_type=""),
                    then=F("outcome_type"),
                ),
                default=Value("Non renseigné"),
                output_field=CharField(),
            )
        )
        .values("victim_type_label")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    by_category = {
        "Hommes": victims.filter(masculin_q).filter(
            Q(victim_age__gte=18)
            | Q(victim_age__isnull=True)
            | Q(victim_age=0)
        ).count(),
        "Femmes": victims.filter(feminin_q).filter(
            Q(victim_age__gte=18)
            | Q(victim_age__isnull=True)
            | Q(victim_age=0)
        ).count(),
        "Garçons": victims.filter(
            masculin_q,
            victim_age__gt=0,
            victim_age__lt=18,
        ).count(),
        "Filles": victims.filter(
            feminin_q,
            victim_age__gt=0,
            victim_age__lt=18,
        ).count(),
        "Non renseigné": victims.exclude(masculin_q | feminin_q).count(),
    }

    age_groups = {
        "0-5 ans": victims.filter(victim_age__gt=0, victim_age__lte=5).count(),
        "6-14 ans": victims.filter(victim_age__range=(6, 14)).count(),
        "15-17 ans": victims.filter(victim_age__range=(15, 17)).count(),
        "18-24 ans": victims.filter(victim_age__range=(18, 24)).count(),
        "25-49 ans": victims.filter(victim_age__range=(25, 49)).count(),
        "50 ans et +": victims.filter(victim_age__gte=50).count(),
        "Non renseigné": victims.filter(
            Q(victim_age__isnull=True) | Q(victim_age=0)
        ).count(),
    }

    professions = (
        victims.annotate(
            profession_label=Case(
                When(
                    Q(profession_before__isnull=False)
                    & ~Q(profession_before=""),
                    then=F("profession_before"),
                ),
                default=Value("Non renseigné"),
                output_field=CharField(),
            )
        )
        .values("profession_label")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    filter_queryset = get_user_scoped_victim_queryset(request.user).filter(
        status=Victim.STATUS_APPROVED
    )

    organisations = (
        filter_queryset.exclude(reporting_org__isnull=True)
        .exclude(reporting_org="")
        .annotate(org_clean=Lower(Trim("reporting_org")))
        .values_list("org_clean", flat=True)
        .distinct()
        .order_by("org_clean")
    )

    accident_types = (
        filter_queryset.annotate(
            accident_type_label=Case(
                When(
                    Q(accident__category__isnull=False)
                    & ~Q(accident__category=""),
                    then=F("accident__category"),
                ),
                When(
                    Q(alpc_type__isnull=False)
                    & ~Q(alpc_type=""),
                    then=F("alpc_type"),
                ),
                default=Value("ALPC"),
                output_field=CharField(),
            )
        )
        .values_list("accident_type_label", flat=True)
        .distinct()
        .order_by("accident_type_label")
    )

    regions = (
        filter_queryset.exclude(region__isnull=True)
        .values("region_id", "region__name")
        .distinct()
        .order_by("region__name")
    )

    cercles = (
        filter_queryset.exclude(cercle__isnull=True)
        .values("cercle_id", "cercle__name")
        .distinct()
        .order_by("cercle__name")
    )

    communes = (
        filter_queryset.exclude(commune__isnull=True)
        .values("commune_id", "commune__name")
        .distinct()
        .order_by("commune__name")
    )

    years = (
        filter_queryset.exclude(report_date__isnull=True)
        .dates("report_date", "year", order="DESC")
    )

    context = {
        "total": total,
        "masculin": masculin,
        "feminin": feminin,
        "masculin_pct": masculin_pct,
        "feminin_pct": feminin_pct,
        "organisations": organisations,
        "accident_types": accident_types,
        "regions": regions,
        "cercles": cercles,
        "communes": communes,
        "years": years,
        "selected_organisation": organisation,
        "selected_accident_type": accident_type,
        "selected_region": region,
        "selected_cercle": cercle,
        "selected_commune": commune,
        "selected_periode": periode,
        "by_accident_type_json": json.dumps(
            list(by_accident_type),
            ensure_ascii=False,
        ),
        "by_status_json": json.dumps(
            list(by_status),
            ensure_ascii=False,
        ),
        "by_category_json": json.dumps(
            by_category,
            ensure_ascii=False,
        ),
        "age_groups_json": json.dumps(
            age_groups,
            ensure_ascii=False,
        ),
        "professions_json": json.dumps(
            list(professions),
            ensure_ascii=False,
        ),
    }

    return render(request, "victims/victim_dashboard.html", context)



def victim_cercle_heatmap(request):
    victims = get_user_scoped_victim_queryset(request.user).filter(
        status=Victim.STATUS_APPROVED
    )

    organisation = request.GET.get("organisation", "").strip()
    accident_type = request.GET.get("accident_type", "").strip()
    cercle = request.GET.get("cercle", "").strip()
    commune = request.GET.get("commune", "").strip()

    filter_queryset = victims

    if organisation and organisation.lower() != "tout":
        victims = victims.annotate(
            org_clean=Lower(Trim("reporting_org"))
        ).filter(
            org_clean=organisation.lower()
        )

    if accident_type and accident_type.lower() != "tout":
        victims = victims.filter(accident__category__iexact=accident_type)

    if cercle and cercle.lower() != "tout":
        if cercle.isdigit():
            victims = victims.filter(cercle_id=cercle)
        else:
            victims = victims.filter(cercle__name__iexact=cercle)

    if commune and commune.lower() != "tout":
        if commune.isdigit():
            victims = victims.filter(commune_id=commune)
        else:
            victims = victims.filter(commune__name__iexact=commune)

    total = victims.count()

    masculin_q = (
        Q(victim_sex__iexact="male")
        | Q(victim_sex__iexact="masculin")
        | Q(victim_sex__iexact="m")
    )

    feminin_q = (
        Q(victim_sex__iexact="female")
        | Q(victim_sex__iexact="féminin")
        | Q(victim_sex__iexact="feminin")
        | Q(victim_sex__iexact="f")
    )

    masculin = victims.filter(masculin_q).count()
    feminin = victims.filter(feminin_q).count()

    masculin_pct = round((masculin / total) * 100, 1) if total else 0
    feminin_pct = round((feminin / total) * 100, 1) if total else 0

        # =========================
    # COORDONNEES TEMPORAIRES
    # =========================

    CERCLE_COORDS = {
        "Bamako": [12.6392, -8.0029],
        "Bandiagara": [14.3500, -3.6100],
        "Douentza": [15.0016, -2.9498],
        "Mopti": [14.4843, -4.1820],
        "Sévaré": [14.5274, -4.0970],
        "Koro": [14.0631, -3.0787],
        "Bankass": [14.0717, -3.5144],
        "Djenné": [13.9061, -4.5533],
        "Ténenkou": [14.4572, -4.9169],
        "Youwarou": [15.3689, -4.2622],
        "Gao": [16.2717, -0.0447],
        "Ansongo": [15.6597, 0.5022],
        "Bourem": [16.9541, -0.3486],
        "Ménaka": [15.9182, 2.4022],
        "Tombouctou": [16.7666, -3.0026],
        "Goundam": [16.4145, -3.6708],
        "Diré": [16.2570, -3.4010],
        "Niafunké": [15.9322, -3.9906],
        "Kayes": [14.4469, -11.4445],
        "Koulikoro": [12.8627, -7.5599],
        "Ségou": [13.4317, -6.2157],
        "Sikasso": [11.3176, -5.6665],
        "Boré": [14.1850, -3.9220],
        "Boni": [15.0700, -2.2200],
        "Aguel-Hoc": [19.4667, 1.4167],
        "Bougouni": [11.4167, -7.4833],
        "Baraouéli": [14.3111, -6.0403],
        "Bla": [12.9442, -5.7561],
        "Macina": [13.9642, -5.3578],
        "Niono": [14.2500, -5.9833],
        "San": [13.3033, -4.8956],
        "Tominian": [13.2878, -3.6767],
        "Mopti": [14.4843, -4.1820],
        "Almoustarat": [17.0500, -0.1500],
        "Goundam": [16.4145, -3.6708],
        "Gourma-Rharous": [16.0833, -1.7667],
        "Niafunké": [15.9322, -3.9906],
    }

    cercles_map = {}

    for v in victims:

        if not v.cercle:
            continue

        lat = None
        lng = None

        # =========================
        # 1. GPS victime
        # =========================
        if (
            v.latitude is not None
            and v.longitude is not None
        ):
            try:
                lat = float(v.latitude)
                lng = float(v.longitude)
            except Exception:
                pass

        # =========================
        # 2. GPS commune
        # =========================
        elif (
            v.commune
            and v.commune.latitude is not None
            and v.commune.longitude is not None
        ):
            lat = float(v.commune.latitude)
            lng = float(v.commune.longitude)

        # =========================
        # 3. GPS cercle
        # =========================
        elif (
            v.cercle
            and v.cercle.latitude is not None
            and v.cercle.longitude is not None
        ):
            lat = float(v.cercle.latitude)
            lng = float(v.cercle.longitude)

        # =========================
        # 4. GPS région
        # =========================
        elif (
            v.region
            and v.region.latitude is not None
            and v.region.longitude is not None
        ):
            lat = float(v.region.latitude)
            lng = float(v.region.longitude)

        # =========================
        # 5. FALLBACK TEMPORAIRE
        # =========================
        elif v.cercle.name in CERCLE_COORDS:
            lat, lng = CERCLE_COORDS[v.cercle.name]

        # =========================
        # AJOUTER SI COORDONNEES
        # =========================
        if lat is None or lng is None:
            continue

        key = v.cercle_id

        if key not in cercles_map:
            cercles_map[key] = {
                "region": v.region.name if v.region else "-",
                "cercle": v.cercle.name,
                "count": 0,
                "lat_sum": 0,
                "lng_sum": 0,
            }

        cercles_map[key]["count"] += 1
        cercles_map[key]["lat_sum"] += lat
        cercles_map[key]["lng_sum"] += lng

    map_data = []

    for item in cercles_map.values():

        count = item["count"]

        map_data.append({
            "region": item["region"],
            "cercle": item["cercle"],
            "count": count,
            "lat": item["lat_sum"] / count,
            "lng": item["lng_sum"] / count,
        })

    organisations = (
        filter_queryset.exclude(reporting_org__isnull=True)
        .exclude(reporting_org="")
        .annotate(org_clean=Lower(Trim("reporting_org")))
        .values_list("org_clean", flat=True)
        .distinct()
        .order_by("org_clean")
    )

    accident_types = (
        filter_queryset.exclude(accident__category__isnull=True)
        .exclude(accident__category="")
        .values_list("accident__category", flat=True)
        .distinct()
        .order_by("accident__category")
    )

    cercles = (
        filter_queryset.exclude(cercle__isnull=True)
        .values("cercle_id", "cercle__name")
        .distinct()
        .order_by("cercle__name")
    )

    communes = (
        filter_queryset.exclude(commune__isnull=True)
        .values("commune_id", "commune__name")
        .distinct()
        .order_by("commune__name")
    )

    context = {
        "total": total,
        "masculin": masculin,
        "feminin": feminin,
        "masculin_pct": masculin_pct,
        "feminin_pct": feminin_pct,
        "organisations": organisations,
        "accident_types": accident_types,
        "cercles": cercles,
        "communes": communes,
        "selected_organisation": organisation,
        "selected_accident_type": accident_type,
        "selected_cercle": cercle,
        "selected_commune": commune,
        "map_data_json": json.dumps(map_data, ensure_ascii=False),
    }

    return render(request, "victims/victim_cercle_heatmap.html", context)


@login_required
def victim_add_assistance_kobo(request, pk):

    victim = get_victim_or_404(request.user, pk)

    if victim.status != Victim.STATUS_APPROVED:
        messages.error(
            request,
            "L’assistance ne peut être ajoutée que lorsque la fiche victime est complètement approuvée.",
        )
        return redirect("victim_detail", pk=victim.pk)

    kobo_url = getattr(settings, "KOBO_ASSISTANCE_FORM_URL", "").strip()

    if not kobo_url:
        messages.error(
            request,
            "Le lien du formulaire Kobo Assistance n’est pas configuré dans settings.py.",
        )
        return redirect("victim_detail", pk=victim.pk)

    accident = victim.accident

    params = urlencode({

        "d[g_identite/accident_id]": (
            safe_get(accident, "reference")
            if accident else ""
        ),

        "d[g_identite/code_victime]": safe_get(
            victim,
            "victim_id"
        ),

        "d[g_identite/nom_victime]": safe_get(
            victim,
            "victim_last_name",
            "last_name"
        ),

        "d[g_identite/prenom_victime]": safe_get(
            victim,
            "victim_first_name",
            "first_name"
        ),

        "d[g_identite/age_victime]": safe_get(
            victim,
            "victim_age",
            "age"
        ),

        "d[g_identite/sexe_victime]": safe_get(
            victim,
            "victim_sex",
            "gender",
            "sex"
        ),

        "d[g_identite/situation_victime]": safe_get(
            victim,
            "outcome_type",
            "victim_type"
        ),

        "d[g_identite/categorie_accident]": (
            safe_get(accident, "category", "accident_type", "type")
            if accident
            else safe_get(victim, "alpc_type")
        ),

        "d[g_identite/date_accident]": (
            format_kobo_date(
                safe_get(
                    accident,
                    "accident_date",
                    "date_accident",
                    "incident_date",
                    "event_date",
                )
            )
            if accident
            else ""
        ),

        "d[g_identite/date_rapportage]": format_kobo_date(
            safe_get(
                victim,
                "report_date",
                "reported_at",
                "submitted_at_kobo",
            )
        ),
    })

    separator = "&" if "?" in kobo_url else "?"
    final_url = f"{kobo_url}{separator}{params}"

    return redirect(final_url)

@login_required
def victim_resubmit(request, pk):
    victim = get_victim_or_404(pk)

    if request.user != victim.created_by and not request.user.is_superuser:
        messages.error(request, "Non autorisé.")
        return redirect("victim_detail", pk=pk)

    if victim.status != Victim.STATUS_RETURNED_FOR_CORRECTION:
        messages.error(request, "Cette fiche victime ne peut pas être ressoumise.")
        return redirect("victim_detail", pk=pk)

    victim.transition_to(
        Victim.STATUS_SUBMITTED,
        user=request.user,
        comment="Fiche victime corrigée et ressoumise.",
    )

    notify_victim_submitted(victim)

    messages.success(request, "La fiche victime a été ressoumise avec succès.")
    return redirect("victim_detail", pk=pk)