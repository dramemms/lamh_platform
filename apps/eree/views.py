import json
from collections import defaultdict

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.permissions import (
    can_approve,
    can_edit_accident,
    can_program_validate,
    can_tech_validate,
)
from apps.notifications.services import (
    notify_eree_submitted,
    notify_eree_tech_validated,
    notify_eree_program_validated,
    notify_eree_returned,
    notify_eree_approved,
)

from .forms import EREESessionForm, EREESessionEditForm
from .models import EREESession, EREESessionChangeLog


# ==========================================================
# OUTILS
# ==========================================================

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


def get_workflow_step_label(session):
    status_map = {
        EREESession.STATUS_DRAFT: "Brouillon",
        EREESession.STATUS_SUBMITTED: "Soumission",
        EREESession.STATUS_TECH_VALIDATED: "Validation technique",
        EREESession.STATUS_PROGRAM_VALIDATED: "Validation programme",
        EREESession.STATUS_APPROVED: "Approbation finale",
    }
    return status_map.get(session.status, session.get_status_display())


def get_eree_queryset():
    return EREESession.objects.select_related(
        "region",
        "cercle",
        "commune",
        "tech_validated_by",
        "program_validated_by",
        "approved_by",
        "created_by",
    )


def get_eree_or_404(pk):
    return get_object_or_404(
        get_eree_queryset().prefetch_related("change_logs"),
        pk=pk,
    )


# ==========================================================
# LISTE
# ==========================================================

@login_required
def eree_list(request):
    query = request.GET.get("q", "").strip()
    selected_region = request.GET.get("region", "").strip()
    selected_cercle = request.GET.get("cercle", "").strip()
    selected_commune = request.GET.get("commune", "").strip()
    status = request.GET.get("status", "").strip()

    base_queryset = EREESession.objects.select_related("region", "cercle", "commune")
    sessions = base_queryset

    if query:
        sessions = sessions.filter(
            Q(reference__icontains=query)
            | Q(title__icontains=query)
            | Q(organisation__icontains=query)
            | Q(reported_by__icontains=query)
            | Q(village__icontains=query)
            | Q(narrative_description__icontains=query)
            | Q(quality_observations__icontains=query)
            | Q(difficulties_solutions__icontains=query)
        )

    if selected_region:
        sessions = sessions.filter(region__name__icontains=selected_region)

    if selected_cercle:
        sessions = sessions.filter(cercle__name__icontains=selected_cercle)

    if selected_commune:
        sessions = sessions.filter(commune__name__icontains=selected_commune)

    allowed_statuses = {
        EREESession.STATUS_DRAFT,
        EREESession.STATUS_SUBMITTED,
        EREESession.STATUS_TECH_VALIDATED,
        EREESession.STATUS_PROGRAM_VALIDATED,
        EREESession.STATUS_APPROVED,
    }

    if status in allowed_statuses:
        sessions = sessions.filter(status=status)
    else:
        status = ""

    sessions = sessions.order_by("-session_date", "-created_at")

    context = {
        "sessions": sessions,
        "count": sessions.count(),
        "count_all": base_queryset.count(),
        "count_draft": base_queryset.filter(status=EREESession.STATUS_DRAFT).count(),
        "count_submitted": base_queryset.filter(status=EREESession.STATUS_SUBMITTED).count(),
        "count_tech": base_queryset.filter(status=EREESession.STATUS_TECH_VALIDATED).count(),
        "count_program": base_queryset.filter(status=EREESession.STATUS_PROGRAM_VALIDATED).count(),
        "count_approved": base_queryset.filter(status=EREESession.STATUS_APPROVED).count(),
        "query": query,
        "selected_region": selected_region,
        "selected_cercle": selected_cercle,
        "selected_commune": selected_commune,
        "current_status": status,
    }

    return render(request, "eree/eree_list.html", context)


# ==========================================================
# DETAIL
# ==========================================================

@login_required
def eree_detail(request, pk):
    session = get_eree_or_404(pk)

    context = {
        "session": session,
        "can_edit": can_edit_accident(request.user),
        "can_tech_validate": can_tech_validate(request.user),
        "can_program_validate": can_program_validate(request.user),
        "can_approve": can_approve(request.user),
    }

    return render(request, "eree/eree_detail.html", context)


# ==========================================================
# AJOUT
# ==========================================================

@login_required
def eree_add(request):
    if not can_edit_accident(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_list")

    if request.method == "POST":
        form = EREESessionForm(request.POST)

        if form.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user

            if not session.status:
                session.status = EREESession.STATUS_SUBMITTED

            session.save()
            form.save_m2m()

            notify_eree_submitted(session)

            messages.success(request, "Activité EREE ajoutée avec succès.")
            return redirect("eree_detail", pk=session.pk)

        messages.error(request, "Le formulaire contient des erreurs.")
    else:
        form = EREESessionForm()

    return render(
        request,
        "eree/eree_form.html",
        {
            "form": form,
            "page_title": "Nouvelle activité EREE",
            "submit_label": "Enregistrer",
        },
    )


# ==========================================================
# MODIFICATION
# ==========================================================

@login_required
def eree_edit(request, pk):
    session = get_eree_or_404(pk)

    if not can_edit_accident(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_detail", pk=pk)

    if session.status == EREESession.STATUS_APPROVED:
        messages.error(request, "Activité déjà approuvée.")
        return redirect("eree_detail", pk=pk)

    if request.method == "POST":
        form = EREESessionEditForm(request.POST, instance=session)

        if form.is_valid():
            comment = form.cleaned_data.get("comment", "").strip()

            old_session = EREESession.objects.get(pk=session.pk)
            workflow_step = get_workflow_step_label(old_session)
            changes = []

            updated_session = form.save(commit=False)

            for field in form.fields:
                if field == "comment":
                    continue

                old_val = getattr(old_session, field, None)
                new_val = getattr(updated_session, field, None)

                if normalize_value(old_val) != normalize_value(new_val):
                    field_label = form.fields[field].label or field
                    changes.append(
                        {
                            "field": field_label,
                            "old": display_value(old_val),
                            "new": display_value(new_val),
                        }
                    )

            if not changes:
                messages.info(request, "Aucune modification détectée.")
                return redirect("eree_detail", pk=pk)

            updated_session.save()
            form.save_m2m()

            for change in changes:
                EREESessionChangeLog.objects.create(
                    session=updated_session,
                    changed_by=request.user,
                    workflow_step=workflow_step,
                    field_name=change["field"],
                    old_value=change["old"],
                    new_value=change["new"],
                    comment=comment or "-",
                )

            messages.success(request, "Modification effectuée.")
            return redirect("eree_detail", pk=pk)

        messages.error(request, "Formulaire invalide.")
    else:
        form = EREESessionEditForm(instance=session)

    return render(
        request,
        "eree/eree_form.html",
        {
            "form": form,
            "session": session,
            "page_title": "Modifier activité EREE",
            "submit_label": "Mettre à jour",
        },
    )


# ==========================================================
# WORKFLOW EREE
# Workflow corrigé :
# SUBMITTED -> TECH_VALIDATED -> PROGRAM_VALIDATED -> APPROVED
# ==========================================================

@login_required
def eree_tech_validate(request, pk):
    session = get_eree_or_404(pk)

    if not can_tech_validate(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_detail", pk=pk)

    if session.status != EREESession.STATUS_SUBMITTED:
        messages.error(request, "Transition invalide.")
        return redirect("eree_detail", pk=pk)

    session.transition_to(EREESession.STATUS_TECH_VALIDATED, user=request.user)
    notify_eree_tech_validated(session)

    messages.success(request, "Validation technique effectuée. La session est maintenant transmise au Programme Manager.")
    return redirect("eree_detail", pk=pk)


@login_required
def eree_program_validate(request, pk):
    session = get_eree_or_404(pk)

    if not can_program_validate(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_detail", pk=pk)

    if session.status != EREESession.STATUS_TECH_VALIDATED:
        messages.error(request, "Transition invalide.")
        return redirect("eree_detail", pk=pk)

    session.transition_to(EREESession.STATUS_PROGRAM_VALIDATED, user=request.user)
    notify_eree_program_validated(session)

    messages.success(request, "Validation programme effectuée. La session attend l'approbation finale.")
    return redirect("eree_detail", pk=pk)


@login_required
def eree_approve(request, pk):
    session = get_eree_or_404(pk)

    if not can_approve(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_detail", pk=pk)

    if session.status != EREESession.STATUS_PROGRAM_VALIDATED:
        messages.error(request, "Transition invalide.")
        return redirect("eree_detail", pk=pk)

    session.transition_to(EREESession.STATUS_APPROVED, user=request.user)
    notify_eree_approved(session)

    messages.success(request, "Activité EREE approuvée définitivement.")
    return redirect("eree_detail", pk=pk)


@login_required
def eree_tech_reject(request, pk):
    session = get_object_or_404(EREESession, pk=pk)

    if not can_tech_validate(request.user):
        messages.error(request, "Action non autorisée.")
        return redirect("eree_detail", pk=pk)

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        if not reason:
            messages.error(request, "Le motif de rejet / retour est obligatoire.")
        else:
            session.transition_to(
                EREESession.STATUS_RETURNED_FOR_CORRECTION,
                user=request.user,
                reason=reason,
                comment=reason,
            )

            notify_eree_returned(session)

            messages.success(
                request,
                "La session EREE a été retournée au soumissionnaire pour correction.",
            )
            return redirect("eree_detail", pk=pk)

    return render(request, "eree/eree_workflow_form.html", {
        "session": session,
        "action": "tech_reject",
    })


@login_required
def eree_program_reject(request, pk):
    session = get_eree_or_404(pk)

    if not can_program_validate(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_detail", pk=pk)

    if session.status != EREESession.STATUS_TECH_VALIDATED:
        messages.error(request, "Transition invalide.")
        return redirect("eree_detail", pk=pk)

    session.transition_to(
        EREESession.STATUS_TECH_VALIDATED,
        user=request.user,
        comment="Retour à la validation technique",
    )

    notify_eree_returned(session)

    messages.warning(request, "Session retournée à la validation technique.")
    return redirect("eree_detail", pk=pk)


# Ancienne vue conservée pour éviter une erreur si l'URL existe encore.
# Elle ne change plus le statut : après validation technique, le Programme Manager peut valider directement.
@login_required
def eree_send_to_program(request, pk):
    session = get_eree_or_404(pk)

    if not can_tech_validate(request.user):
        messages.error(request, "Non autorisé.")
        return redirect("eree_detail", pk=pk)

    if session.status != EREESession.STATUS_TECH_VALIDATED:
        messages.error(request, "Transition invalide.")
        return redirect("eree_detail", pk=pk)

    notify_eree_tech_validated(session)
    messages.success(request, "Notification envoyée au Programme Manager.")
    return redirect("eree_detail", pk=pk)


# ==========================================================
# EXPORT EXCEL
# ==========================================================

@login_required
def export_eree_excel(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    sessions = get_eree_queryset().all()

    if query:
        sessions = sessions.filter(
            Q(reference__icontains=query)
            | Q(title__icontains=query)
            | Q(organisation__icontains=query)
            | Q(reported_by__icontains=query)
            | Q(village__icontains=query)
        )

    if status:
        sessions = sessions.filter(status=status)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "EREE"

    excluded_fields = ["raw_payload"]
    fields = [f for f in EREESession._meta.fields if f.name not in excluded_fields]

    headers = [f.verbose_name.title() for f in fields]
    ws.append(headers)

    for obj in sessions:
        row = []

        for field in fields:
            value = getattr(obj, field.name, "")

            if field.name == "status":
                try:
                    value = obj.get_status_display()
                except Exception:
                    value = str(value)
            elif hasattr(value, "name"):
                value = value.name
            elif hasattr(value, "username"):
                value = value.username
            elif hasattr(value, "strftime"):
                value = value.strftime("%d/%m/%Y %H:%M")
            else:
                value = str(value) if value is not None else ""

            row.append(value)

        ws.append(row)

    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass

        ws.column_dimensions[col_letter].width = min(max_length + 2, 60)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="eree.xlsx"'

    wb.save(response)
    return response


# ==========================================================
# DASHBOARD EREE
# ==========================================================


def eree_dashboard(request, template_name="eree/eree_dashboard.html"):
    sessions = EREESession.objects.select_related(
        "region", "cercle", "commune"
    ).filter(status=EREESession.STATUS_APPROVED)

    organisation = request.GET.get("organisation", "").strip()
    funding_source = request.GET.get("funding_source", "").strip()
    session_type = request.GET.get("session_type", "").strip()
    region = request.GET.get("region", "").strip()
    cercle = request.GET.get("cercle", "").strip()
    commune = request.GET.get("commune", "").strip()
    periode = request.GET.get("periode", "").strip()

    if organisation:
        sessions = sessions.filter(organisation=organisation)

    if funding_source:
        sessions = sessions.filter(funding_type=funding_source)

    if session_type:
        sessions = sessions.filter(sensitization_type=session_type)

    if region:
        sessions = sessions.filter(region_id=region)

    if cercle:
        sessions = sessions.filter(cercle_id=cercle)

    if commune:
        sessions = sessions.filter(commune_id=commune)

    if periode and periode.isdigit():
        sessions = sessions.filter(session_date__year=int(periode))

    total_sessions = sessions.count()
    total_beneficiaries = sum(s.total_participants or 0 for s in sessions)

    humanitarian_male = sum(s.humanitarian_male or 0 for s in sessions)
    humanitarian_female = sum(s.humanitarian_female or 0 for s in sessions)

    pdi_boys = sum(
        (s.pdi_boys_0_5 or 0)
        + (s.pdi_boys_6_14 or 0)
        + (s.pdi_boys_15_17 or 0)
        for s in sessions
    )

    pdi_girls = sum(
        (s.pdi_girls_0_5 or 0)
        + (s.pdi_girls_6_14 or 0)
        + (s.pdi_girls_15_17 or 0)
        for s in sessions
    )

    pdi_men = sum(
        (s.pdi_men_18_24 or 0)
        + (s.pdi_men_25_49 or 0)
        + (s.pdi_men_50_59 or 0)
        + (s.pdi_men_60_plus or 0)
        for s in sessions
    )

    pdi_women = sum(
        (s.pdi_women_18_24 or 0)
        + (s.pdi_women_25_49 or 0)
        + (s.pdi_women_50_59 or 0)
        + (s.pdi_women_60_plus or 0)
        for s in sessions
    )

    ch_boys = sum(
        (s.ch_boys_0_5 or 0)
        + (s.ch_boys_6_14 or 0)
        + (s.ch_boys_15_17 or 0)
        for s in sessions
    )

    ch_girls = sum(
        (s.ch_girls_0_5 or 0)
        + (s.ch_girls_6_14 or 0)
        + (s.ch_girls_15_17 or 0)
        for s in sessions
    )

    ch_men = sum(
        (s.ch_men_18_24 or 0)
        + (s.ch_men_25_49 or 0)
        + (s.ch_men_50_59 or 0)
        + (s.ch_men_60_plus or 0)
        for s in sessions
    )

    ch_women = sum(
        (s.ch_women_18_24 or 0)
        + (s.ch_women_25_49 or 0)
        + (s.ch_women_50_59 or 0)
        + (s.ch_women_60_plus or 0)
        for s in sessions
    )

    total_male = humanitarian_male + pdi_boys + pdi_men + ch_boys + ch_men
    total_female = humanitarian_female + pdi_girls + pdi_women + ch_girls + ch_women

    total_boys = pdi_boys + ch_boys
    total_girls = pdi_girls + ch_girls
    total_men = humanitarian_male + pdi_men + ch_men
    total_women = humanitarian_female + pdi_women + ch_women

    male_pct = round((total_male / total_beneficiaries * 100), 1) if total_beneficiaries else 0
    female_pct = round((total_female / total_beneficiaries * 100), 1) if total_beneficiaries else 0

    sessions_chart = (
        sessions.values("sensitization_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    funding_chart = (
        sessions.values("funding_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    map_cercles = (
        sessions.exclude(cercle__isnull=True)
        .values("cercle__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    age_groups = {
        "0-5 ans": sum(
            (s.pdi_boys_0_5 or 0) + (s.pdi_girls_0_5 or 0)
            + (s.ch_boys_0_5 or 0) + (s.ch_girls_0_5 or 0)
            for s in sessions
        ),
        "6-14 ans": sum(
            (s.pdi_boys_6_14 or 0) + (s.pdi_girls_6_14 or 0)
            + (s.ch_boys_6_14 or 0) + (s.ch_girls_6_14 or 0)
            for s in sessions
        ),
        "15-17 ans": sum(
            (s.pdi_boys_15_17 or 0) + (s.pdi_girls_15_17 or 0)
            + (s.ch_boys_15_17 or 0) + (s.ch_girls_15_17 or 0)
            for s in sessions
        ),
        "18-24 ans": sum(
            (s.pdi_men_18_24 or 0) + (s.pdi_women_18_24 or 0)
            + (s.ch_men_18_24 or 0) + (s.ch_women_18_24 or 0)
            for s in sessions
        ),
        "25-49 ans": sum(
            (s.pdi_men_25_49 or 0) + (s.pdi_women_25_49 or 0)
            + (s.ch_men_25_49 or 0) + (s.ch_women_25_49 or 0)
            for s in sessions
        ),
        "50 ans et +": sum(
            (s.pdi_men_50_59 or 0) + (s.pdi_women_50_59 or 0)
            + (s.pdi_men_60_plus or 0) + (s.pdi_women_60_plus or 0)
            + (s.ch_men_50_59 or 0) + (s.ch_women_50_59 or 0)
            + (s.ch_men_60_plus or 0) + (s.ch_women_60_plus or 0)
            for s in sessions
        ),
    }

    status_data = {
        "PDI": pdi_boys + pdi_girls + pdi_men + pdi_women,
        "Communauté hôte": ch_boys + ch_girls + ch_men + ch_women,
        "Travailleurs humanitaires": humanitarian_male + humanitarian_female,
    }

    category_data = {
        "Hommes": total_men,
        "Femmes": total_women,
        "Garçons": total_boys,
        "Filles": total_girls,
    }

    humanitarian_data = {
        "Hommes": humanitarian_male,
        "Femmes": humanitarian_female,
    }

    civil_subcategories = [
        {"label": "PDI - Hommes", "total": pdi_men},
        {"label": "PDI - Femmes", "total": pdi_women},
        {"label": "PDI - Garçons", "total": pdi_boys},
        {"label": "PDI - Filles", "total": pdi_girls},
        {"label": "Communauté hôte - Hommes", "total": ch_men},
        {"label": "Communauté hôte - Femmes", "total": ch_women},
        {"label": "Communauté hôte - Garçons", "total": ch_boys},
        {"label": "Communauté hôte - Filles", "total": ch_girls},
    ]

    filter_queryset = EREESession.objects.filter(status=EREESession.STATUS_APPROVED)

    context = {
        "total_sessions": total_sessions,
        "total_beneficiaries": total_beneficiaries,
        "total_male": total_male,
        "total_female": total_female,
        "male_pct": male_pct,
        "female_pct": female_pct,
        "total_boys": total_boys,
        "total_girls": total_girls,
        "total_men": total_men,
        "total_women": total_women,

        "organisations": filter_queryset.exclude(organisation__isnull=True).exclude(organisation="").values_list("organisation", flat=True).distinct().order_by("organisation"),
        "funding_sources": filter_queryset.exclude(funding_type__isnull=True).exclude(funding_type="").values_list("funding_type", flat=True).distinct().order_by("funding_type"),
        "session_types": filter_queryset.exclude(sensitization_type__isnull=True).exclude(sensitization_type="").values_list("sensitization_type", flat=True).distinct().order_by("sensitization_type"),
        "regions": filter_queryset.exclude(region__isnull=True).values("region_id", "region__name").distinct().order_by("region__name"),
        "cercles": filter_queryset.exclude(cercle__isnull=True).values("cercle_id", "cercle__name").distinct().order_by("cercle__name"),
        "communes": filter_queryset.exclude(commune__isnull=True).values("commune_id", "commune__name").distinct().order_by("commune__name"),
        "years": filter_queryset.exclude(session_date__isnull=True).dates("session_date", "year", order="DESC"),

        "selected_organisation": organisation,
        "selected_funding_source": funding_source,
        "selected_session_type": session_type,
        "selected_region": region,
        "selected_cercle": cercle,
        "selected_commune": commune,
        "selected_periode": periode,

        "sessions_labels_json": json.dumps([x["sensitization_type"] or "Non défini" for x in sessions_chart], ensure_ascii=False),
        "sessions_values_json": json.dumps([x["total"] for x in sessions_chart], ensure_ascii=False),

        "funding_labels_json": json.dumps([x["funding_type"] or "Non défini" for x in funding_chart], ensure_ascii=False),
        "funding_values_json": json.dumps([x["total"] for x in funding_chart], ensure_ascii=False),

        "map_cercle_labels_json": json.dumps([x["cercle__name"] or "Non défini" for x in map_cercles], ensure_ascii=False),
        "map_cercle_values_json": json.dumps([x["total"] for x in map_cercles], ensure_ascii=False),

        "age_groups_json": json.dumps(age_groups, ensure_ascii=False),
        "status_json": json.dumps(status_data, ensure_ascii=False),
        "category_json": json.dumps(category_data, ensure_ascii=False),
        "humanitarian_json": json.dumps(humanitarian_data, ensure_ascii=False),
        "civil_subcategories": civil_subcategories,
    }

    return render(request, template_name, context)


def eree_dashboard_page2(request):
    return eree_dashboard(request, template_name="eree/eree_dashboard_page2.html")
