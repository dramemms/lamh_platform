from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML, CSS


from apps.incidents.forms import AccidentForm
from apps.incidents.models import Accident
from apps.victims.models import Victim
from apps.eree.models import EREESession
from apps.geo.models import Region, Cercle, Commune

def rate(part, total):
    if not total:
        return 0
    return round((part / total) * 100, 1)


def home(request):
    return render(request, "home.html")



def dashboard(request):
    accidents_count = Accident.objects.count()
    victims_count = Victim.objects.count()
    eree_count = EREESession.objects.count()

    submissions_count = accidents_count + victims_count + eree_count

    context = {
        "accidents_count": accidents_count,
        "victims_count": victims_count,
        "eree_count": eree_count,
        "submissions_count": submissions_count,
    }

    return render(request, "dashboard.html", context)


@login_required
def export_lamh_dashboard_pdf(request):
    accidents_count = Accident.objects.count()
    victims_count = Victim.objects.count()
    eree_count = EREESession.objects.count()

    accidents_approved = Accident.objects.filter(status="APPROVED").count()
    victims_approved = Victim.objects.filter(status="APPROVED").count()

    # IMPORTANT : EREE utilise session_status
    eree_approved = EREESession.objects.filter(session_status="APPROVED").count()

    accidents_pending = accidents_count - accidents_approved
    victims_pending = victims_count - victims_approved
    eree_pending = eree_count - eree_approved

    context = {
        "generated_at": timezone.now(),

        "total_records": accidents_count + victims_count + eree_count,

        "accidents_count": accidents_count,
        "accidents_approved": accidents_approved,
        "accidents_pending": accidents_pending,
        "accidents_approval_rate": rate(accidents_approved, accidents_count),

        "victims_count": victims_count,
        "victims_approved": victims_approved,
        "victims_pending": victims_pending,
        "victims_approval_rate": rate(victims_approved, victims_count),

        "eree_count": eree_count,
        "eree_approved": eree_approved,
        "eree_pending": eree_pending,
        "eree_approval_rate": rate(eree_approved, eree_count),
    }

    html_string = render_to_string(
        "core/dashboard_pdf.html",
        context,
        request=request,
    )

    response = HttpResponse(content_type="application/pdf")
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

@login_required
def data_management(request):
    context = {
        "accidents_count": Accident.objects.count(),
        "victims_count": Victim.objects.count(),
        "eree_count": EREESession.objects.count(),
        "regions_count": Region.objects.count(),
        "cercles_count": Cercle.objects.count(),
        "communes_count": Commune.objects.count(),
    }
    return render(request, "core/data_management.html", context)

# =====================================================
# GESTION ACCIDENTS
# =====================================================

@login_required
def manage_accidents(request):

    accidents = Accident.objects.all().order_by("-id")

    return render(
        request,
        "core/manage_accidents.html",
        {
            "accidents": accidents
        }
    )


@login_required
def edit_accident(request, pk):

    accident = get_object_or_404(
        Accident,
        pk=pk
    )

    if request.method == "POST":

        form = AccidentForm(
            request.POST,
            instance=accident
        )

        if form.is_valid():

            form.save()

            return redirect("manage_accidents")

    else:

        form = AccidentForm(
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


@login_required
def delete_accident(request, pk):

    accident = get_object_or_404(
        Accident,
        pk=pk
    )

    if request.method == "POST":

        accident.delete()

        return redirect("manage_accidents")

    return render(
        request,
        "core/delete_accident.html",
        {
            "accident": accident
        }
    )