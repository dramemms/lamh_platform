import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.incidents.models import Accident
from apps.geo.models import Region, Cercle, Commune
from .models import Victim


def to_bool(value):
    if value is None:
        return False
    return str(value).strip().lower() in ["yes", "true", "1", "oui", "o"]


def to_int(value):
    try:
        if value in [None, ""]:
            return None
        return int(value)
    except Exception:
        return None


def parse_gps(value):
    """
    Kobo geopoint :
    'latitude longitude altitude precision'
    Exemple : '13.12345 -7.12345 0 5'
    """
    if not value:
        return None, None

    try:
        parts = str(value).strip().split()
        if len(parts) >= 2:
            latitude = float(parts[0])
            longitude = float(parts[1])
            return latitude, longitude
    except Exception:
        pass

    return None, None


def get_obj_by_code_or_name(model, value):
    """
    Recherche dans Region/Cercle/Commune par code ou par nom.
    """
    if not value:
        return None

    value = str(value).strip()

    obj = model.objects.filter(code=value).first()
    if obj:
        return obj

    obj = model.objects.filter(name__iexact=value).first()
    if obj:
        return obj

    return None


def get_geo_coordinates(region=None, cercle=None, commune=None):
    """
    Récupère les coordonnées depuis la base geo.
    Priorité :
    1. Commune
    2. Cercle
    3. Région
    """

    if commune:
        lat = getattr(commune, "latitude", None)
        lon = getattr(commune, "longitude", None)
        if lat and lon:
            return lat, lon

    if cercle:
        lat = getattr(cercle, "latitude", None)
        lon = getattr(cercle, "longitude", None)
        if lat and lon:
            return lat, lon

    if region:
        lat = getattr(region, "latitude", None)
        lon = getattr(region, "longitude", None)
        if lat and lon:
            return lat, lon

    return None, None


@csrf_exempt
@require_POST
def kobo_victim_webhook(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    print("=== KOBO VICTIM WEBHOOK ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    accident_ref = (
    data.get("g_report/accident_id")
    or data.get("accident_id")
    or data.get("g_identite/accident_id")
    or data.get("id_accident")
    or data.get("g_report/id_accident")
    or data.get("accident_reference")
)
    print("Référence accident reçue :", accident_ref)

    if not accident_ref:
        return JsonResponse({"error": "accident_id manquant"}, status=400)

    accident = Accident.objects.filter(reference=accident_ref).first()
    print("Accident trouvé :", accident)

    if not accident:
        return JsonResponse({"error": "Accident introuvable"}, status=400)

    # Localisation Kobo
    region_value = data.get("g_location/region")
    cercle_value = data.get("g_location/cercle")
    commune_value = data.get("g_location/commune")

    region = get_obj_by_code_or_name(Region, region_value)
    cercle = get_obj_by_code_or_name(Cercle, cercle_value)
    commune = get_obj_by_code_or_name(Commune, commune_value)

    gps_value = (
        data.get("g_location/location_gps")
        or data.get("g_location/gps")
        or data.get("location_gps")
        or data.get("gps")
    )

    latitude, longitude = parse_gps(gps_value)

    # Si Kobo n'a pas envoyé GPS, on récupère depuis la base geo
    if not latitude or not longitude:
        latitude, longitude = get_geo_coordinates(
            region=region,
            cercle=cercle,
            commune=commune,
        )

    try:
        victim = Victim.objects.create(
            accident=accident,
            accident_reference=accident_ref,

            victim_id=data.get("g_report/victim_id"),
            report_date=data.get("g_report/report_date"),

            reported_by=data.get("g_report/reported_by"),
            reporting_org=data.get("g_report/reporting_org"),
            reporting_position=data.get("g_report/reporting_position"),
            reporting_team=data.get("g_report/reporting_team"),

            consentement=to_bool(data.get("g_victim/consentement")),

            victim_last_name=data.get("g_victim/victim_last_name"),
            victim_first_name=data.get("g_victim/victim_first_name"),

            victim_type=data.get("g_victim/victim_type"),
            father_name=data.get("g_victim/father_name"),
            mother_name=data.get("g_victim/mother_name"),

            nationality=data.get("g_victim/nationality"),
            marital_status=data.get("g_victim/marital_status"),

            profession_before=data.get("g_victim/profession_before"),
            profession_after=data.get("g_victim/profession_after"),

            outcome_type=data.get("g_victim/outcome_type"),

            birth_date_known=to_bool(data.get("g_victim/birth_date_known")),
            birth_date=data.get("g_victim/birth_date"),
            victim_age=to_int(data.get("g_victim/victim_age")),
            victim_sex=data.get("g_victim/victim_sex"),

            main_breadwinner=to_bool(data.get("g_victim/main_breadwinner")),
            dependents_count=to_int(data.get("g_victim/dependents_count")),

            urgent_medical_evac=to_bool(data.get("g_victim/urgent_medical_evac")),

            victim_contact=data.get("g_victim/victim_contact"),

            activity_at_accident=data.get("g_victim/activity_at_accident"),

            knew_danger_zone=to_bool(data.get("g_victim/knew_danger_zone")),
            reason_enter_zone=data.get("g_victim/reason_enter_zone"),
            times_entered_zone=to_int(data.get("g_victim/times_entered_zone")),

            saw_object=to_bool(data.get("g_victim/saw_object")),

            blast_cause=data.get("g_victim/blast_cause"),
            alpc_type=data.get("g_victim/alpc_type"),

            received_er_before=to_bool(data.get("g_victim/received_er_before")),
            received_er_after=to_bool(data.get("g_victim/received_er_after")),

            pre_existing_disability=to_bool(data.get("g_victim/pre_existing_disability")),

            health_structure=data.get("g_victim/health_structure"),
            medical_care=to_bool(data.get("g_victim/medical_care")),
            non_medical_care=to_bool(data.get("g_victim/non_medical_care")),

            info_source=data.get("g_source/info_source"),
            source_age=to_int(data.get("g_source/source_age")),
            source_last_name=data.get("g_source/source_last_name"),
            source_first_name=data.get("g_source/source_first_name"),
            source_contact=data.get("g_source/source_contact"),
            source_sex=data.get("g_source/source_sex"),

            country=data.get("g_location/country"),
            region=region,
            cercle=cercle,
            commune=commune,
            village=(
                data.get("g_location/village")
                or data.get("g_location/village_quartier")
                or data.get("g_location/localite")
            ),

            location_gps=gps_value,
            latitude=latitude,
            longitude=longitude,

            kobo_submission_id=data.get("_id"),
            kobo_uuid=data.get("_uuid"),
            raw_payload=data,
        )

        return JsonResponse({
            "status": "success",
            "victim_id": victim.id,
            "latitude": latitude,
            "longitude": longitude,
            "source_coordinates": "kobo_gps" if gps_value else "geo_database",
        })

    except Exception as e:
        print("Erreur création victime :", str(e))
        return JsonResponse({"error": str(e)}, status=400)