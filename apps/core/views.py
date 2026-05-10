from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)




from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from weasyprint import HTML, CSS

from apps.incidents.forms import AccidentEditForm
from apps.incidents.models import Accident

from apps.victims.models import Victim
from apps.victims.forms import VictimEditForm
from apps.eree.models import EREESession
from apps.eree.forms import EREEEditForm

from apps.geo.models import (
    Region,
    Cercle,
    Commune
)


def rate(part, total):

    if not total:
        return 0

    return round((part / total) * 100, 1)


# =====================================================
# HOME
# =====================================================

def home(request):

    return render(
        request,
        "home.html"
    )


# =====================================================
# DASHBOARD
# =====================================================

def dashboard(request):

    accidents_count = Accident.objects.count()

    victims_count = Victim.objects.count()

    eree_count = EREESession.objects.count()

    submissions_count = (
        accidents_count
        + victims_count
        + eree_count
    )

    context = {

        "accidents_count": accidents_count,

        "victims_count": victims_count,

        "eree_count": eree_count,

        "submissions_count": submissions_count,
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =====================================================
# EXPORT PDF DASHBOARD
# =====================================================

@login_required
def export_lamh_dashboard_pdf(request):

    accidents_count = Accident.objects.count()

    victims_count = Victim.objects.count()

    eree_count = EREESession.objects.count()

    accidents_approved = Accident.objects.filter(
        status="APPROVED"
    ).count()

    victims_approved = Victim.objects.filter(
        status="APPROVED"
    ).count()

    eree_approved = EREESession.objects.filter(
        session_status="APPROVED"
    ).count()

    accidents_pending = (
        accidents_count
        - accidents_approved
    )

    victims_pending = (
        victims_count
        - victims_approved
    )

    eree_pending = (
        eree_count
        - eree_approved
    )

    context = {

        "generated_at": timezone.now(),

        "total_records":
            accidents_count
            + victims_count
            + eree_count,

        # ACCIDENTS
        "accidents_count": accidents_count,
        "accidents_approved": accidents_approved,
        "accidents_pending": accidents_pending,
        "accidents_approval_rate":
            rate(
                accidents_approved,
                accidents_count
            ),

        # VICTIMS
        "victims_count": victims_count,
        "victims_approved": victims_approved,
        "victims_pending": victims_pending,
        "victims_approval_rate":
            rate(
                victims_approved,
                victims_count
            ),

        # EREE
        "eree_count": eree_count,
        "eree_approved": eree_approved,
        "eree_pending": eree_pending,
        "eree_approval_rate":
            rate(
                eree_approved,
                eree_count
            ),
    }

    html_string = render_to_string(
        "core/dashboard_pdf.html",
        context,
        request=request,
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="rapport_dashboard_lamh.pdf"'
    )

    HTML(
        string=html_string,
        base_url=request.build_absolute_uri(),
    ).write_pdf(
        response,
        stylesheets=[
            CSS(
                string="""
                @page {
                    size: A4 landscape;
                    margin: 1.2cm;
                }
                """
            )
        ],
    )

    return response


# =====================================================
# GESTION DES DONNEES
# =====================================================

@login_required
def data_management(request):

    context = {

        "accidents_count":
            Accident.objects.count(),

        "victims_count":
            Victim.objects.count(),

        "eree_count":
            EREESession.objects.count(),

        "regions_count":
            Region.objects.count(),

        "cercles_count":
            Cercle.objects.count(),

        "communes_count":
            Commune.objects.count(),
    }

    return render(
        request,
        "core/data_management.html",
        context
    )


# =====================================================
# GESTION ACCIDENTS
# =====================================================

@login_required
def manage_accidents(request):

    accidents = (
        Accident.objects
        .all()
        .order_by("-id")
    )

    return render(
        request,
        "core/manage_accidents.html",
        {
            "accidents": accidents
        }
    )


# =====================================================
# MODIFIER ACCIDENT
# =====================================================

@login_required
def edit_accident(request, pk):

    accident = get_object_or_404(
        Accident,
        pk=pk
    )

    if request.method == "POST":

        form = AccidentEditForm(
            request.POST,
            instance=accident
        )

        if form.is_valid():

            form.save()

            return redirect(
                "manage_accidents"
            )

    else:

        form = AccidentEditForm(
            instance=accident
        )

    return render(
        request,
        "core/edit_accident.html",
        {
            "form": form,
            "accident": accident
        }
    )


# =====================================================
# SUPPRIMER ACCIDENT
# =====================================================

@login_required
def delete_accident(request, pk):

    accident = get_object_or_404(
        Accident,
        pk=pk
    )

    if request.method == "POST":

        accident.delete()

        return redirect(
            "manage_accidents"
        )

    return render(
        request,
        "core/delete_accident.html",
        {
            "accident": accident
        }
    )

# =====================================================
# GESTION VICTIMES
# =====================================================

@login_required
def manage_victims(request):
    victims = Victim.objects.all().order_by("-id")

    return render(
        request,
        "core/manage_victims.html",
        {"victims": victims}
    )


@login_required
def edit_victim(request, pk):
    victim = get_object_or_404(Victim, pk=pk)

    if request.method == "POST":
        form = VictimEditForm(request.POST, instance=victim)

        if form.is_valid():
            form.save()
            return redirect("manage_victims")

    else:
        form = VictimEditForm(instance=victim)

    return render(
        request,
        "core/edit_victim.html",
        {
            "form": form,
            "victim": victim
        }
    )


@login_required
def delete_victim(request, pk):
    victim = get_object_or_404(Victim, pk=pk)

    if request.method == "POST":
        victim.delete()
        return redirect("manage_victims")

    return render(
        request,
        "core/delete_victim.html",
        {"victim": victim}
    )


# =====================================================
# GESTION EREE
# =====================================================

@login_required
def manage_eree(request):
    sessions = EREESession.objects.all().order_by("-id")

    return render(
        request,
        "core/manage_eree.html",
        {"sessions": sessions}
    )


@login_required
def edit_eree(request, pk):
    session = get_object_or_404(EREESession, pk=pk)

    if request.method == "POST":
        form = EREEEditForm(request.POST, instance=session)

        if form.is_valid():
            form.save()
            return redirect("manage_eree")

    else:
        form = EREEEditForm(instance=session)

    return render(
        request,
        "core/edit_eree.html",
        {
            "form": form,
            "session": session
        }
    )


@login_required
def delete_eree(request, pk):
    session = get_object_or_404(EREESession, pk=pk)

    if request.method == "POST":
        session.delete()
        return redirect("manage_eree")

    return render(
        request,
        "core/delete_eree.html",
        {"session": session}
    )

# =====================================================
# GESTION REGIONS
# =====================================================

@login_required
def manage_regions(request):
    regions = Region.objects.all().order_by("name")
    return render(request, "core/manage_regions.html", {"regions": regions})


# =====================================================
# GESTION CERCLES
# =====================================================

@login_required
def manage_cercles(request):
    cercles = Cercle.objects.select_related("region").all().order_by("region__name", "name")
    return render(request, "core/manage_cercles.html", {"cercles": cercles})


# =====================================================
# GESTION COMMUNES
# =====================================================

@login_required
def manage_communes(request):
    communes = Commune.objects.select_related("cercle", "cercle__region").all().order_by(
        "cercle__region__name",
        "cercle__name",
        "name"
    )
    return render(request, "core/manage_communes.html", {"communes": communes})