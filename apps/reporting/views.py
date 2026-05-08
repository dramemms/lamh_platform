import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import PAIAssistanceSubmission
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from openpyxl import Workbook

from collections import Counter
import json



def reporting_home(request):
    submissions = PAIAssistanceSubmission.objects.all()

    q = request.GET.get("q", "").strip().lower()
    assistance_type = request.GET.get("type_assistance", "").strip().lower()
    region = request.GET.get("region", "").strip().lower()
    cercle = request.GET.get("cercle", "").strip().lower()

    if q or assistance_type or region or cercle:
        filtered = []

        for s in submissions:
            data = s.raw_data or {}

            code_victime = str(data.get("g_identite/code_victime", "")).lower()
            nom = str(data.get("g_identite/nom_victime", "")).lower()
            prenom = str(data.get("g_identite/prenom_victime", "")).lower()
            type_assistance_value = str(data.get("g_assistance/type_assistance", "")).lower()
            region_value = str(data.get("g_localisation/region", "")).lower()
            cercle_value = str(data.get("g_localisation/cercle", "")).lower()

            match_q = (
                not q
                or q in code_victime
                or q in nom
                or q in prenom
            )

            match_type = (
                not assistance_type
                or assistance_type in type_assistance_value
            )

            match_region = (
                not region
                or region in region_value
            )

            match_cercle = (
                not cercle
                or cercle in cercle_value
            )

            if match_q and match_type and match_region and match_cercle:
                filtered.append(s)

        submissions = filtered

    return render(request, "reporting/home.html", {
        "submissions": submissions,
        "q": request.GET.get("q", ""),
        "type_assistance": request.GET.get("type_assistance", ""),
        "region": request.GET.get("region", ""),
        "cercle": request.GET.get("cercle", ""),
    })


def assistance_form(request):
    return render(request, "reporting/assistance_form.html")


@csrf_exempt
def kobo_pai_webhook(request):

    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        print("===== WEBHOOK KOBO PAI =====")
        print(data)

        PAIAssistanceSubmission.objects.create(
            victim_code=data.get("code_victime") or data.get("d/code_victime"),
            victim_name=data.get("nom_victime") or data.get("d/nom_victime"),
            assistance_type=data.get("type_assistance") or data.get("d/type_assistance"),
            raw_data=data,
        )

        return JsonResponse({
            "status": "success",
            "message": "Données Kobo enregistrées avec succès"
        })

    return JsonResponse({
        "status": "ok",
        "message": "Webhook PAI actif"
    })

def assistance_detail(request, pk):

    submission = get_object_or_404(PAIAssistanceSubmission, pk=pk)

    return render(request, "reporting/assistance_detail.html", {
        "submission": submission
    })

def export_assistance_excel(request):

    submissions = PAIAssistanceSubmission.objects.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Assistance Victimes"

    headers = [

        # IDENTITÉ
        "Code victime",
        "Nom victime",
        "Prénom victime",
        "Âge victime",
        "Sexe victime",
        "Situation victime",
        "Catégorie accident",
        "Date accident",
        "Date rapportage",

        # LOCALISATION
        "Région",
        "Cercle",
        "Commune",
        "Village / Quartier",
        "Coordonnées GPS",

        # BENEFICIAIRE
        "Victime directe",
        "Nom bénéficiaire",
        "Prénom bénéficiaire",
        "Catégorie bénéficiaire",
        "Nom victime directe",
        "Prénom victime directe",
        "Numéro bénéficiaire",
        "Lien avec victime",
        "Téléphone / Orange Money",
        "Justification transfert",

        # ASSISTANCE
        "Catégorie assistance",
        "Type assistance",
        "Précision référencement",
        "Structure référencement",
        "Date référencement",
        "Nom point focal",
        "Contact point focal",
        "Date suivi 1",
        "Date suivi 2",
        "Date suivi 3",
        "Date suivi 4",
        "Date début assistance",
        "Date fin assistance",
        "Coût assistance",
        "Devise",
        "Statut transfert",
        "Réception confirmée",
        "Usage transfert",
        "Moyen évacuation",
        "Prestataire prise en charge",
        "Préciser structure",
        "Mode paiement",
        "Point A",
        "Point B",
        "Temps évacuation",
        "Structure prise en charge",
        "Soins urgence",
        "Type soins",
        "Référence reçu",
        "Référencement externe",
        "Type référencement",
        "Préciser référencement",
        "Date référencement externe",
        "Nom PF externe",
        "Contact PF externe",
        "Date suivi ext 1",
        "Date suivi ext 2",
        "Date suivi ext 3",
        "Date suivi ext 4",
        "Observations",

        # CLOTURE
        "Date ouverture",
        "Date clôture",
        "Statut cas",
        "Niveau satisfaction",
        "Motif clôture",
        "Niveau résolution",
        "Commentaires",

        # SYSTEME
        "Date réception Kobo",

    ]

    ws.append(headers)

    for s in submissions:

        data = s.raw_data or {}

        row = [

            # IDENTITE
            data.get("g_identite/code_victime", ""),
            data.get("g_identite/nom_victime", ""),
            data.get("g_identite/prenom_victime", ""),
            data.get("g_identite/age_victime", ""),
            data.get("g_identite/sexe_victime", ""),
            data.get("g_identite/situation_victime", ""),
            data.get("g_identite/categorie_accident", ""),
            data.get("g_identite/date_accident", ""),
            data.get("g_identite/date_rapportage", ""),

            # LOCALISATION
            data.get("g_localisation/region", ""),
            data.get("g_localisation/cercle", ""),
            data.get("g_localisation/commune", ""),
            data.get("g_localisation/village_quartier", ""),
            data.get("g_localisation/coordonnees_gps", ""),

            # BENEFICIAIRE
            data.get("g_beneficiaire/victime_directe", ""),
            data.get("g_beneficiaire/nom_beneficiaire", ""),
            data.get("g_beneficiaire/prenom_beneficiaire", ""),
            data.get("g_beneficiaire/categorie_beneficiaire", ""),
            data.get("g_beneficiaire/nom_victime_directe", ""),
            data.get("g_beneficiaire/prenom_victime_directe", ""),
            data.get("g_beneficiaire/numero_beneficiaire", ""),
            data.get("g_beneficiaire/lien_victime", ""),
            data.get("g_beneficiaire/telephone_orange_money", ""),
            data.get("g_beneficiaire/justification_transfert", ""),

            # ASSISTANCE
            data.get("g_assistance/categorie_assistance", ""),
            data.get("g_assistance/type_assistance", ""),
            data.get("g_assistance/type_referencement_precision", ""),
            data.get("g_assistance/structure_referencement", ""),
            data.get("g_assistance/date_referencement", ""),
            data.get("g_assistance/nom_point_focal", ""),
            data.get("g_assistance/contact_point_focal", ""),
            data.get("g_assistance/date_suivi_1", ""),
            data.get("g_assistance/date_suivi_2", ""),
            data.get("g_assistance/date_suivi_3", ""),
            data.get("g_assistance/date_suivi_4", ""),
            data.get("g_assistance/date_debut_assistance", ""),
            data.get("g_assistance/date_fin_assistance", ""),
            data.get("g_assistance/cout_assistance", ""),
            data.get("g_assistance/devise", ""),
            data.get("g_assistance/statut_transfert", ""),
            data.get("g_assistance/reception_confirmee", ""),
            data.get("g_assistance/usage_transfert", ""),
            data.get("g_assistance/moyen_evacuation", ""),
            data.get("g_assistance/prestataire_prise_charge", ""),
            data.get("g_assistance/preciser_structure", ""),
            data.get("g_assistance/mode_paiement", ""),
            data.get("g_assistance/point_a", ""),
            data.get("g_assistance/point_b", ""),
            data.get("g_assistance/temps_evacuation", ""),
            data.get("g_assistance/structure_prise_charge", ""),
            data.get("g_assistance/soins_urgence", ""),
            data.get("g_assistance/type_soins", ""),
            data.get("g_assistance/reference_recu", ""),
            data.get("g_assistance/referencement_externe", ""),
            data.get("g_assistance/type_referencement", ""),
            data.get("g_assistance/preciser_referencement", ""),
            data.get("g_assistance/date_referencement_externe", ""),
            data.get("g_assistance/nom_pf_externe", ""),
            data.get("g_assistance/contact_pf_externe", ""),
            data.get("g_assistance/date_suivi_ext_1", ""),
            data.get("g_assistance/date_suivi_ext_2", ""),
            data.get("g_assistance/date_suivi_ext_3", ""),
            data.get("g_assistance/date_suivi_ext_4", ""),
            data.get("g_assistance/observations", ""),

            # CLOTURE
            data.get("g_cloture/date_ouverture", ""),
            data.get("g_cloture/date_cloture", ""),
            data.get("g_cloture/statut_cas", ""),
            data.get("g_cloture/niveau_satisfaction", ""),
            data.get("g_cloture/motif_cloture", ""),
            data.get("g_cloture/niveau_resolution", ""),
            data.get("g_cloture/commentaires", ""),

            # SYSTEME
            s.submitted_at.strftime("%d/%m/%Y %H:%M") if s.submitted_at else "",

        ]

        ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="assistance_victimes.xlsx"'
    )

    wb.save(response)

    return response

def assistance_dashboard(request):
    submissions = PAIAssistanceSubmission.objects.all()

    categorie_assistance = request.GET.get("categorie_assistance", "")
    type_assistance = request.GET.get("type_assistance", "")
    mode_paiement = request.GET.get("mode_paiement", "")
    cercle_filter = request.GET.get("cercle", "")

    # Options filtres avant filtrage
    all_data = [s.raw_data or {} for s in submissions]

    categories_assistance = sorted(set(
        d.get("g_assistance/categorie_assistance", "")
        for d in all_data if d.get("g_assistance/categorie_assistance", "")
    ))

    types_assistance = sorted(set(
        d.get("g_assistance/type_assistance", "")
        for d in all_data if d.get("g_assistance/type_assistance", "")
    ))

    modes_paiement = sorted(set(
        d.get("g_assistance/mode_paiement", "")
        for d in all_data if d.get("g_assistance/mode_paiement", "")
    ))

    cercles = sorted(set(
        d.get("g_localisation/cercle", "")
        for d in all_data if d.get("g_localisation/cercle", "")
    ))

    # Filtrage
    filtered = []

    for s in submissions:
        data = s.raw_data or {}

        if categorie_assistance and data.get("g_assistance/categorie_assistance", "") != categorie_assistance:
            continue

        if type_assistance and data.get("g_assistance/type_assistance", "") != type_assistance:
            continue

        if mode_paiement and data.get("g_assistance/mode_paiement", "") != mode_paiement:
            continue

        if cercle_filter and data.get("g_localisation/cercle", "") != cercle_filter:
            continue

        filtered.append(s)

    submissions = filtered

    total_assistances = len(submissions)
    total_victimes = len(set(
        (s.raw_data or {}).get("g_identite/code_victime", "")
        for s in submissions
        if (s.raw_data or {}).get("g_identite/code_victime", "")
    ))

    total_hommes = 0
    total_femmes = 0

    type_counter = Counter()
    categorie_counter = Counter()
    paiement_counter = Counter()
    cercle_counter = Counter()

    heatmap_points = []

    for s in submissions:
        data = s.raw_data or {}

        sexe = data.get("g_identite/sexe_victime", "").lower()

        if sexe == "masculin":
            total_hommes += 1
        elif sexe == "feminin" or sexe == "féminin":
            total_femmes += 1

        type_counter[data.get("g_assistance/type_assistance", "Non défini")] += 1
        categorie_counter[data.get("g_assistance/categorie_assistance", "Non défini")] += 1
        paiement_counter[data.get("g_assistance/mode_paiement", "Non défini")] += 1

        cercle = data.get("g_localisation/cercle", "Non défini")
        cercle_counter[cercle] += 1

        gps = data.get("g_localisation/coordonnees_gps", "")

        if gps:
            try:
                parts = str(gps).split()
                lat = float(parts[0])
                lng = float(parts[1])

                heatmap_points.append({
                    "lat": lat,
                    "lng": lng,
                    "cercle": cercle,
                    "count": 1,
                })
            except:
                pass

    context = {
        "submissions": submissions,

        "total_assistances": total_assistances,
        "total_victimes": total_victimes,
        "total_hommes": total_hommes,
        "total_femmes": total_femmes,

        "categories_assistance": categories_assistance,
        "types_assistance": types_assistance,
        "modes_paiement": modes_paiement,
        "cercles": cercles,

        "type_labels": json.dumps(list(type_counter.keys())),
        "type_values": json.dumps(list(type_counter.values())),

        "categorie_labels": json.dumps(list(categorie_counter.keys())),
        "categorie_values": json.dumps(list(categorie_counter.values())),

        "paiement_labels": json.dumps(list(paiement_counter.keys())),
        "paiement_values": json.dumps(list(paiement_counter.values())),

        "heatmap_points": json.dumps(heatmap_points),
    }

    return render(request, "reporting/assistance_dashboard.html", context)